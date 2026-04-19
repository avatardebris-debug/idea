"""
pipeline/runner.py
Main entry point — subprocess orchestrator for the multi-agent pipeline.

Starts each agent as a subprocess, monitors health, handles shutdown.

Usage:
    python pipeline/runner.py "Build a web scraper for Hacker News"
    python pipeline/runner.py --from-list
    python pipeline/runner.py --resume
    python pipeline/runner.py --from-list --provider ollama --model qwen3.5:35b --time-limit 480
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import signal
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timezone

# Ensure project root is on path
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.message_bus import MessageBus, Message

# Anchor PIPELINE_DIR to where this script lives (project root), not cwd.
# This prevents /workspace/.pipeline vs /.pipeline splits when the user
# starts the runner from different directories.
PIPELINE_DIR = PROJECT_ROOT.resolve() / ".pipeline"
AGENTS_DIR = pathlib.Path(__file__).parent / "agents"

# All agent roles and their module paths
AGENT_ROLES = [
    "idea_planner",
    "phase_planner",
    "executor",
    "validator",
    "reviewer",
    "manager",
    "ideator",
]


# ---------------------------------------------------------------------------
# Pipeline state management
# ---------------------------------------------------------------------------

def init_pipeline_dirs() -> None:
    """Create all pipeline runtime directories."""
    for subdir in ["queues", "state", "projects", "logs"]:
        (PIPELINE_DIR / subdir).mkdir(parents=True, exist_ok=True)


def _slugify(title: str) -> str:
    """Convert an idea title to a filesystem-safe slug.
    'CSV Analyzer' -> 'csv_analyzer', '[Youtube studio]' -> 'youtube_studio'
    """
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_-]+', '_', slug)
    return slug.strip('_') or "unknown"


def _get_active_idea_state(pipeline_dir: pathlib.Path) -> dict:
    """Return the current_idea.json from the most recently modified project.

    Falls back to the old global .pipeline/state/current_idea.json for
    backwards compatibility with runs that predate the per-project isolation.
    """
    projects_dir = pipeline_dir / "projects"
    candidates: list[pathlib.Path] = []

    if projects_dir.exists():
        candidates = list(projects_dir.glob("*/state/current_idea.json"))

    if candidates:
        newest = max(candidates, key=lambda p: p.stat().st_mtime)
        try:
            state = json.loads(newest.read_text(encoding="utf-8"))
            state.setdefault("_slug", newest.parent.parent.name)
            return state
        except Exception:
            pass

    # Fallback: old global location (pre-isolation runs)
    old_path = pipeline_dir / "state" / "current_idea.json"
    if old_path.exists():
        try:
            return json.loads(old_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {}


def save_pipeline_status(status: dict) -> None:
    path = PIPELINE_DIR / "state" / "pipeline_status.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)


def load_pipeline_status() -> dict:
    path = PIPELINE_DIR / "state" / "pipeline_status.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


# ---------------------------------------------------------------------------
# Agent subprocess management
# ---------------------------------------------------------------------------

class AgentSupervisor:
    """Manages agent subprocesses."""

    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        self.processes: dict[str, subprocess.Popen] = {}
        self._stop_requested = False

    def start_agent(self, role: str) -> subprocess.Popen:
        """Start an agent as a subprocess."""
        module_path = AGENTS_DIR / f"{role}.py"
        if not module_path.exists():
            raise FileNotFoundError(f"Agent module not found: {module_path}")

        cmd = [
            sys.executable, str(module_path),
            "--provider", self.provider,
            "--model", self.model,
        ]

        # Set up environment with project root on PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        env["PYTHONUTF8"] = "1"

        log_path = PIPELINE_DIR / "logs" / f"{role}.out"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = open(log_path, "a", encoding="utf-8")

        proc = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            # On Windows, use CREATE_NEW_PROCESS_GROUP for clean shutdown
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        log_file.close()  # child inherited the handle; parent must close its copy

        self.processes[role] = proc
        return proc

    def start_all(self) -> None:
        """Start all agent subprocesses."""
        for role in AGENT_ROLES:
            self.start_agent(role)
            print(f"  ✓ Started {role} (PID {self.processes[role].pid})")
            time.sleep(0.5)  # stagger starts slightly

    def stop_all(self) -> None:
        """Gracefully stop all agent subprocesses."""
        self._stop_requested = True

        # Send shutdown signal via message bus
        bus = MessageBus()
        for role in AGENT_ROLES:
            bus.send_signal("runner", role, "SHUTDOWN")

        # Wait up to 10 seconds for graceful shutdown
        deadline = time.time() + 10
        for role, proc in self.processes.items():
            remaining = max(0, deadline - time.time())
            try:
                proc.wait(timeout=remaining)
                print(f"  ✓ {role} stopped gracefully")
            except subprocess.TimeoutExpired:
                print(f"  ⚠ {role} didn't stop, killing...")
                proc.kill()
                proc.wait(timeout=5)

    def check_health(self) -> dict[str, str]:
        """Check which agents are running."""
        status = {}
        for role, proc in self.processes.items():
            ret = proc.poll()
            if ret is None:
                status[role] = "running"
            else:
                status[role] = f"exited({ret})"
        return status

    def restart_dead(self) -> list[str]:
        """Restart any agents that have died unexpectedly."""
        restarted = []
        for role, proc in list(self.processes.items()):
            if proc.poll() is not None and not self._stop_requested:
                print(f"  ⚠ {role} died (exit={proc.returncode}), restarting...")
                self.start_agent(role)
                restarted.append(role)
                time.sleep(1)
        return restarted

    def save_registry(self) -> None:
        """Write current agent state to registry file."""
        registry = {}
        for role, proc in self.processes.items():
            registry[role] = {
                "pid": proc.pid,
                "status": "running" if proc.poll() is None else f"exited({proc.returncode})",
            }
        path = PIPELINE_DIR / "state" / "agent_registry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)


# ---------------------------------------------------------------------------
# Seed the pipeline with the first idea
# ---------------------------------------------------------------------------

_seeded_this_session: set[str] = set()  # titles seeded in this runner invocation


def seed_idea(bus: MessageBus, title: str, description: str) -> None:
    """Send the initial idea to the Idea Planner to kick off the pipeline."""
    if title in _seeded_this_session:
        return  # already seeded this run — don't duplicate
    _seeded_this_session.add(title)

    idea_slug = _slugify(title)

    msg = Message.create(
        from_agent="runner",
        to_agent="idea_planner",
        type="task",
        payload={
            "title": title,
            "idea": description,
            "idea_slug": idea_slug,
        },
    )
    bus.send(msg)
    print(f"\n  📋 Seeded idea: {title} (slug: {idea_slug})")


def seed_from_master_list(bus: MessageBus) -> bool:
    """Find the first unchecked idea in master_ideas.md and seed it.

    Skips ideas that already have project state (in-progress or completed)
    so partial projects can resume naturally from restored queues.
    """
    mi_path = PROJECT_ROOT.resolve() / "master_ideas.md"
    if not mi_path.exists():
        print("  ✗ master_ideas.md not found")
        return False

    import re
    content = mi_path.read_text(encoding="utf-8")
    for line in content.split("\n"):
        match = re.match(r"- \[ \]\s+\*\*(.+?)\*\*\s*[—–-]\s*(.*)", line)
        if match:
            title = match.group(1).strip()
            if title in _seeded_this_session:
                continue  # already in progress this session — skip

            slug = _slugify(title)
            project_state = PIPELINE_DIR / "projects" / slug / "state" / "current_idea.json"

            if project_state.exists():
                # Project already has work done — skip seeding, let queues resume it.
                # If queues are empty and it's stuck, the user can delete the state
                # to force a re-seed: rm .pipeline/projects/<slug>/state/current_idea.json
                try:
                    state = json.loads(project_state.read_text(encoding="utf-8"))
                    status = state.get("status", "?")
                    if status != "complete":
                        print(f"  ⏭  Skipping '{title}' — already in progress ({status}), resuming from queue")
                        _seeded_this_session.add(title)  # don't try again this session
                        continue
                    else:
                        # Completed — skip entirely
                        _seeded_this_session.add(title)
                        continue
                except Exception:
                    pass  # Can't read state — seed it fresh

            description = match.group(2).strip()
            seed_idea(bus, title, description)
            return True

    print("  ✗ No unchecked ideas found in master_ideas.md")
    return False


def check_resume(bus: MessageBus) -> bool:
    """Check if there's an active pipeline state to resume."""
    status = load_pipeline_status()
    if status.get("status") == "running":
        print(f"  🔄 Resuming pipeline (idea: {status.get('current_idea', '?')})")
        return True

    # Check if any queues have pending messages
    for role in AGENT_ROLES:
        if bus.queue_depth(role) > 0:
            print(f"  🔄 Found pending messages in {role} queue — resuming")
            return True

    return False

def _rebuild_queues_from_state(bus: MessageBus) -> int:
    """Re-inject queue messages for in-progress projects that have no queued work.

    This enables resume from a zip: if .pipeline/projects/ was restored but
    .pipeline/queues/ was not (or was empty), this reconstructs the correct
    messages so agents can pick up where they left off.

    Returns the number of projects re-queued.
    """
    if bus.has_active_work():
        return 0  # Queues are already populated — nothing to rebuild

    projects_dir = PIPELINE_DIR / "projects"
    if not projects_dir.exists():
        return 0

    injected = 0
    for project_dir in sorted(projects_dir.iterdir()):
        if not project_dir.is_dir():
            continue

        state_file = project_dir / "state" / "current_idea.json"
        if not state_file.exists():
            continue

        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        status = state.get("status", "")
        title  = state.get("title", project_dir.name)
        slug   = project_dir.name

        if status in ("", "complete"):
            continue

        # Detect which phase and step we were on
        phase_match = re.match(r"phase_(\d+)_(\w+)", status)
        if phase_match:
            phase_num  = int(phase_match.group(1))
            phase_step = phase_match.group(2)
        elif status == "planning":
            # Was in initial idea planning — restart from idea_planner
            msg = Message.create(
                from_agent="runner",
                to_agent="idea_planner",
                type="task",
                payload={
                    "title": title,
                    "idea": state.get("description", title),
                    "idea_slug": slug,
                },
            )
            bus.send(msg)
            injected += 1
            print(f"  🔁 Re-queued '{title}' → idea_planner (was: planning)")
            continue
        else:
            continue  # Unknown status — skip

        tasks_path     = f"phases/phase_{phase_num}/tasks.md"
        workspace_path = str(project_dir / "workspace")
        report_path    = f"phases/phase_{phase_num}/validation_report.md"
        review_path    = f"phases/phase_{phase_num}/review.md"

        # Route to the correct agent based on phase step
        if phase_step == "planning":
            # phase_planner was building the task list
            master_plan_file = project_dir / "state" / "master_plan.md"
            phase_spec = master_plan_file.read_text(encoding="utf-8")[:500] \
                if master_plan_file.exists() else f"Resume phase {phase_num} of {title}"
            agent    = "phase_planner"
            payload  = {"phase": phase_num, "phase_spec": phase_spec, "idea_slug": slug}
        elif phase_step == "executing":
            agent   = "executor"
            payload = {"phase": phase_num, "tasks_path": tasks_path,
                       "workspace_path": workspace_path, "idea_slug": slug}
        elif phase_step == "validating":
            agent   = "validator"
            payload = {"phase": phase_num, "tasks_path": tasks_path,
                       "workspace_path": workspace_path,
                       "validation_report_path": report_path, "idea_slug": slug}
        elif phase_step == "reviewing":
            agent   = "reviewer"
            payload = {"phase": phase_num, "tasks_path": tasks_path,
                       "workspace_path": workspace_path,
                       "validation_report_path": report_path,
                       "review_path": review_path, "idea_slug": slug}
        else:
            continue  # Unknown step

        bus.send(Message.create(from_agent="runner", to_agent=agent,
                                type="task", payload=payload))
        injected += 1
        print(f"  🔁 Re-queued '{title}' → {agent} (was: {status})")

    return injected



def run_pipeline(
    idea: str | None = None,
    from_list: bool = False,
    resume: bool = False,
    provider: str = "ollama",
    model: str = "qwen3.5:35b",
    time_limit_minutes: float = 0,
) -> None:
    """Main pipeline orchestrator."""
    init_pipeline_dirs()
    bus = MessageBus()

    print("=" * 60)
    print("  🏭 Idea Development Pipeline")
    print("=" * 60)
    print(f"  Provider: {provider}")
    print(f"  Model:    {model}")
    if time_limit_minutes > 0:
        print(f"  Time:     {time_limit_minutes:.0f} minutes")
    else:
        print(f"  Time:     unlimited")
    print(f"  Agents:   {len(AGENT_ROLES)}")

    # Determine what to work on
    has_work = False

    if resume:
        has_work = check_resume(bus)
        if not has_work:
            # Queues empty but project state may exist — try rebuilding from state
            rebuilt = _rebuild_queues_from_state(bus)
            if rebuilt:
                print(f"  🔄 Rebuilt queues for {rebuilt} project(s) from saved state")
                has_work = True
            else:
                print("  No active pipeline to resume.")

    if not has_work and idea:
        seed_idea(bus, idea.split(".")[0][:50], idea)
        has_work = True

    if not has_work and from_list:
        # First try to rebuild any in-progress projects from saved state
        rebuilt = _rebuild_queues_from_state(bus)
        if rebuilt:
            print(f"  🔄 Rebuilt queues for {rebuilt} project(s) from saved state")
            has_work = True
        else:
            has_work = seed_from_master_list(bus)

    if not has_work:
        print("\n  ✗ Nothing to do. Provide an idea, use --from-list, or --resume.")
        print("    python pipeline/runner.py \"Your idea here\"")
        print("    python pipeline/runner.py --from-list")
        return

    # Save initial status
    save_pipeline_status({
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "current_idea": idea or "(from list)",
    })

    # Start all agents
    print(f"\n  Starting agents...")
    supervisor = AgentSupervisor(provider, model)

    # Handle Ctrl+C
    stop_requested = False
    original_sigint = signal.getsignal(signal.SIGINT)

    def _handle_interrupt(signum, frame):
        nonlocal stop_requested
        if stop_requested:
            print("\n  Force stopping...")
            supervisor.stop_all()
            sys.exit(1)
        print("\n\n  [Pipeline] Graceful stop requested. Finishing current work...")
        print("  [Pipeline] Press Ctrl+C again to force stop.")
        stop_requested = True

    signal.signal(signal.SIGINT, _handle_interrupt)

    try:
        supervisor.start_all()
        supervisor.save_registry()

        print(f"\n  🚀 Pipeline running. Press Ctrl+C to stop.\n")

        start_time = time.time()
        health_check_interval = 60  # seconds — agents take minutes per call
        last_health_check = time.time()
        _status_count = 0  # for throttling non-interactive log output

        while not stop_requested:
            # Time limit check
            if time_limit_minutes > 0:
                elapsed = (time.time() - start_time) / 60
                if elapsed >= time_limit_minutes:
                    print(f"\n  ⏰ Time limit reached ({time_limit_minutes:.0f} min)")
                    break

            # Periodic health check
            if time.time() - last_health_check >= health_check_interval:
                health = supervisor.check_health()
                restarted = supervisor.restart_dead()
                if restarted:
                    supervisor.save_registry()

                # Check if all queues are empty AND all ideas done
                all_empty = bus.all_queues_empty()
                # Find the most recently updated project's current_idea.json
                idea_state = _get_active_idea_state(PIPELINE_DIR)

                running_agents = sum(1 for s in health.values() if s == "running")

                # Print status line
                pending_total = sum(bus.queue_depth(r) for r in AGENT_ROLES)
                elapsed_m = (time.time() - start_time) / 60
                phase = idea_state.get("status", "?")
                title = idea_state.get("title", "")
                title_str = f" | {title[:28]}" if title else ""
                status_line = (
                    f"  [{elapsed_m:.0f}m] agents={running_agents}/{len(AGENT_ROLES)} "
                    f"pending={pending_total} phase={phase}{title_str}"
                )
                if sys.stdout.isatty():
                    print(status_line + "    ", end="\r", flush=True)
                else:
                    # Non-interactive (redirected to log) — print every 4 checks
                    if _status_count % 4 == 0:
                        print(status_line, flush=True)
                    _status_count += 1

                if all_empty and not from_list:
                    # Single idea mode — might be done
                    # Wait a bit longer to make sure nothing new arrives
                    time.sleep(10)
                    if bus.all_queues_empty():
                        print(f"\n  ✓ All queues empty — pipeline complete.")
                        break
                elif all_empty and from_list:
                    # Only seed the next idea when the pipeline is truly idle —
                    # i.e. no pending AND no in-flight (processing) messages.
                    # all_queues_empty() only counts 'pending'; has_active_work()
                    # counts both, preventing premature seeding.
                    if not bus.has_active_work():
                        if not seed_from_master_list(bus):
                            print(f"\n  ✓ All ideas processed — pipeline complete.")
                            break

                last_health_check = time.time()

            time.sleep(2)

    finally:
        print("\n  Stopping agents...")
        supervisor.stop_all()
        supervisor.save_registry()

        save_pipeline_status({
            "status": "stopped",
            "stopped_at": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "model": model,
        })

        signal.signal(signal.SIGINT, original_sigint)

        print("\n" + "=" * 60)
        print("  Pipeline stopped.")
        print(f"  Logs: .pipeline/logs/")
        print(f"  Output: .pipeline/workspace/")
        print(f"  Decisions: .pipeline/state/manager_decisions.md")
        print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Multi-agent idea development pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
              python pipeline/runner.py "Build a CLI tool that converts CSV to JSON"
              python pipeline/runner.py --from-list
              python pipeline/runner.py --from-list --provider ollama --model qwen3.5:35b --time-limit 480
              python pipeline/runner.py --resume
        """),
    )
    parser.add_argument("idea", nargs="?", default=None,
                        help="Idea description to implement")
    parser.add_argument("--from-list", action="store_true",
                        help="Read ideas from master_ideas.md")
    parser.add_argument("--resume", action="store_true",
                        help="Resume a previously stopped pipeline")
    parser.add_argument("--provider", default="ollama",
                        choices=["openai", "claude", "gemini", "ollama"],
                        help="LLM provider (default: ollama)")
    parser.add_argument("--model", default="qwen3.5:35b",
                        help="LLM model (default: qwen3.5:35b)")
    parser.add_argument("--time-limit", type=float, default=0,
                        help="Time limit in minutes (0 = unlimited)")

    args = parser.parse_args()

    if not args.idea and not args.from_list and not args.resume:
        parser.print_help()
        print("\nProvide an idea, use --from-list, or --resume.")
        sys.exit(1)

    run_pipeline(
        idea=args.idea,
        from_list=args.from_list,
        resume=args.resume,
        provider=args.provider,
        model=args.model,
        time_limit_minutes=args.time_limit,
    )


if __name__ == "__main__":
    main()
