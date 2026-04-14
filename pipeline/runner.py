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

PIPELINE_DIR = pathlib.Path(".pipeline")
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
    for subdir in ["queues", "state", "phases", "workspace", "ideator_output", "logs"]:
        (PIPELINE_DIR / subdir).mkdir(parents=True, exist_ok=True)


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

    msg = Message.create(
        from_agent="runner",
        to_agent="idea_planner",
        type="task",
        payload={
            "title": title,
            "idea": description,
        },
    )
    bus.send(msg)
    print(f"\n  📋 Seeded idea: {title}")


def seed_from_master_list(bus: MessageBus) -> bool:
    """Find the first unchecked idea in master_ideas.md and seed it."""
    mi_path = pathlib.Path("master_ideas.md")
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



# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

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
            print("  No active pipeline to resume.")

    if not has_work and idea:
        seed_idea(bus, idea.split(".")[0][:50], idea)
        has_work = True

    if not has_work and from_list:
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
                idea_state = {}
                idea_state_path = PIPELINE_DIR / "state" / "current_idea.json"
                if idea_state_path.exists():
                    with open(idea_state_path, encoding="utf-8") as f:
                        idea_state = json.load(f)

                running_agents = sum(1 for s in health.values() if s == "running")

                # Print status line
                pending_total = sum(bus.queue_depth(r) for r in AGENT_ROLES)
                elapsed_m = (time.time() - start_time) / 60
                phase = idea_state.get("status", "?")
                status_line = (
                    f"  [{elapsed_m:.0f}m] agents={running_agents}/{len(AGENT_ROLES)} "
                    f"pending={pending_total} phase={phase}"
                )
                if sys.stdout.isatty():
                    print(status_line + "    ", end="\r", flush=True)
                else:
                    # Non-interactive (redirected to log) — print every 4 checks
                    if getattr(self, "_status_count", 0) % 4 == 0:
                        print(status_line, flush=True)
                    self._status_count = getattr(self, "_status_count", 0) + 1

                if all_empty and not from_list:
                    # Single idea mode — might be done
                    # Wait a bit longer to make sure nothing new arrives
                    time.sleep(10)
                    if bus.all_queues_empty():
                        print(f"\n  ✓ All queues empty — pipeline complete.")
                        break
                elif all_empty and from_list:
                    # Try to start next idea
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
