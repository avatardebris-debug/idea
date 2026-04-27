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

_ANSI_ESCAPE = re.compile(r'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~]|\x1B\][^\x07\x1B]*(?:\x07|\x1B\\))')

def _clean(text: str) -> str:
    """Strip ANSI/OSC escape sequences from a string."""
    return _ANSI_ESCAPE.sub('', text)

# Ensure project root is on path
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.message_bus import MessageBus, Message
from pipeline.metrics import RunMetrics

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


# Maximum wall-clock time per project before force-completing (minutes).
# 90 min = enough for 3 phases × ~25 min each.  Prevents any single project
# from monopolizing an unattended pipeline run.
PROJECT_TIME_BUDGET = 90

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
                    if status in ("complete", "budget_exceeded"):
                        # Finished — skip entirely
                        _seeded_this_session.add(title)
                        continue
                    else:
                        print(f"  ⏭  Skipping '{title}' — already in progress ({status}), resuming from queue")
                        _seeded_this_session.add(title)  # don't try again this session
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
    """Re-inject a queue message for ONE in-progress project that has no queued work.

    Called at startup and during the health-check loop when queues appear empty.
    Re-queues ONE project at a time (matching seed_from_master_list behaviour)
    so the pipeline works serially through incomplete projects rather than
    dumping all of them into the queue at once.

    Also enforces a wall-clock budget per project — any project that has been
    running longer than PROJECT_TIME_BUDGET minutes is force-completed.

    Returns the number of projects re-queued (0 or 1).
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

        if status in ("", "complete", "budget_exceeded"):
            continue

        # --- Budget enforcement: reset started_at to NOW ---
        # Budget measures per-SESSION time, not total project lifetime.
        # On a cold restart, every project's old started_at would be hours
        # old, causing everything to get budget_exceeded immediately.
        # Reset the clock so budget enforcement works correctly during THIS
        # session's health-check loop.
        state["started_at"] = datetime.now(timezone.utc).isoformat()
        state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

        # Skip projects whose validator has already hit the stall limit —
        # these should have been force-advanced by the manager, but if the
        # manager message was lost, don't loop forever on the same project.
        retries_file = project_dir / "state" / "phase_retries.json"
        if retries_file.exists():
            try:
                retries = json.loads(retries_file.read_text(encoding="utf-8"))
                # Check for any no_progress streak >= 2 (our stall limit)
                for k, v in retries.items():
                    if "no_progress" in k and isinstance(v, int) and v >= 2:
                        # Force-mark as complete so it never comes back
                        state["status"] = "complete"
                        state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
                        print(f"  ⏭  Force-completed stalled project '{title}' (stuck {v} cycles)")
                        break
                else:
                    retries = None  # didn't break — not stalled
                if state.get("status") == "complete":
                    continue
            except Exception:
                pass

        # Detect which phase and step we were on
        phase_match = re.match(r"phase_(\d+)_(\w+)", status)
        if phase_match:
            phase_num  = int(phase_match.group(1))
            phase_step = phase_match.group(2)

            # --- Retroactive task guardrail ---
            # Trim oversized task files for projects created before the guardrail.
            MAX_TASKS = 8
            tasks_file = project_dir / f"phases/phase_{phase_num}/tasks.md"
            if tasks_file.exists():
                try:
                    from pipeline.agent_process import AgentProcess
                    raw = tasks_file.read_text(encoding="utf-8")
                    scoped = AgentProcess._extract_phase_tasks(raw, phase_num)
                    lines = scoped.split("\n")
                    task_indices = [i for i, l in enumerate(lines) if l.strip().startswith("- [ ]") or l.strip().startswith("- [x]")]
                    if len(task_indices) > MAX_TASKS:
                        cut_at = task_indices[MAX_TASKS]
                        trimmed = "\n".join(lines[:cut_at])
                        trimmed += f"\n\n<!-- {len(task_indices) - MAX_TASKS} tasks removed by retroactive guardrail -->\n"
                        tasks_file.write_text(trimmed, encoding="utf-8")
                        print(f"  ✂️  Trimmed '{title}' phase {phase_num}: {len(task_indices)} → {MAX_TASKS} tasks")
                except Exception:
                    pass
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
        elif phase_step == "reviewed":
            # Reviewer finished — deterministic routing via _tick_project
            routed = _tick_project(bus, project_dir, state, phase_num, slug)
            if routed:
                return 1
            continue
        else:
            continue  # Unknown step

        bus.send(Message.create(from_agent="runner", to_agent=agent,
                                type="task", payload=payload))
        print(f"  🔁 Re-queued '{title}' → {agent} (was: {status})")
        return 1  # One at a time — next project picked up after this one completes

    return 0  # No incomplete projects found


# Maximum reviewer→executor round-trips per phase before force-advancing
MAX_PHASE_RETRIES = 12


def _tick_project(
    bus: MessageBus,
    project_dir: pathlib.Path,
    state: dict,
    phase_num: int,
    slug: str,
) -> bool:
    """Deterministic state machine tick for a reviewed project.

    Reads the reviewer's verdict from current_idea.json and routes:
    - 0 blocking bugs → advance to next phase (or complete)
    - Blocking bugs → send back to executor (up to MAX_PHASE_RETRIES)
    - Emergency (architectural issues) → re-plan the phase

    Returns True if a message was sent, False if nothing to do.
    """
    review = state.get("review_result", {})
    blocking_bugs = review.get("blocking_bugs", 0)
    review_content = review.get("review_content_preview", "")
    non_blocking_notes = review.get("non_blocking_notes", "")
    tasks_path = review.get("tasks_path", f"phases/phase_{phase_num}/tasks.md")
    workspace_path = review.get("workspace_path", str(project_dir / "workspace"))
    review_path = review.get("review_path", f"phases/phase_{phase_num}/review.md")
    title = state.get("title", slug)

    # Check for emergency rework indicators
    rework_indicators = sum(1 for word in ["fundamental", "architectural",
                                            "completely wrong", "redesign",
                                            "start over", "rewrite"]
                            if word in review_content.lower())
    is_emergency = rework_indicators >= 3 or blocking_bugs > 5

    if is_emergency:
        # EMERGENCY REWORK — re-plan the phase
        review_full = str(project_dir / review_path) if review_path else ""
        bus.send(Message.create(
            from_agent="runner",
            to_agent="phase_planner",
            type="task",
            payload={
                "phase": phase_num,
                "phase_spec": f"REWORK REQUIRED — see review at {review_full}",
                "is_rework": True,
                "idea_slug": slug,
            },
            priority=0,
        ))
        # Update status
        _write_state(project_dir, state, f"phase_{phase_num}_planning")
        print(f"  🚨 Emergency rework for '{title}' phase {phase_num}")
        return True

    elif blocking_bugs > 0:
        # Increment retry counter
        retries = _increment_retries(project_dir, phase_num)

        if retries >= MAX_PHASE_RETRIES:
            # Too many retries — force-advance
            print(f"  ⚠️  Force-advancing '{title}' phase {phase_num} after {retries} retries ({blocking_bugs} bugs remain)")
            _reset_retries(project_dir, phase_num)
            advanced = _advance_phase(bus, project_dir, state, phase_num, slug)
            if not advanced:
                _mark_complete(project_dir, state, title)
            return True
        else:
            # Send back to executor with fix instructions
            review_full = str(project_dir / review_path) if review_path else ""
            bus.send(Message.create(
                from_agent="runner",
                to_agent="executor",
                type="task",
                payload={
                    "phase": phase_num,
                    "tasks_path": tasks_path,
                    "workspace_path": workspace_path,
                    "fix_required": True,
                    "review_path": review_path,
                    "blocking_bugs": blocking_bugs,
                    "fix_instructions": (
                        f"Fix {blocking_bugs} blocking bugs from review (attempt {retries}/{MAX_PHASE_RETRIES}). "
                        f"Read `{review_full}` for details."
                    ),
                    "idea_slug": slug,
                },
            ))
            _write_state(project_dir, state, f"phase_{phase_num}_executing")
            print(f"  🔧 '{title}' phase {phase_num}: {blocking_bugs} bugs → executor (retry {retries}/{MAX_PHASE_RETRIES})")
            return True
    else:
        # Clean pass — save non-blocking notes, advance or complete
        if non_blocking_notes:
            _append_polish(project_dir, phase_num, non_blocking_notes)

        _reset_retries(project_dir, phase_num)

        advanced = _advance_phase(bus, project_dir, state, phase_num, slug)
        if not advanced:
            _mark_complete(project_dir, state, title)
            print(f"  ✅ '{title}' completed all phases!")
        else:
            print(f"  ➡️  '{title}' phase {phase_num} passed → advancing to phase {phase_num + 1}")

        return True


def _advance_phase(
    bus: MessageBus,
    project_dir: pathlib.Path,
    state: dict,
    completed_phase: int,
    slug: str,
) -> bool:
    """Advance to next phase if one exists. Returns True if advanced."""
    master_plan_file = project_dir / "state" / "master_plan.md"
    if not master_plan_file.exists():
        return False

    master_plan = master_plan_file.read_text(encoding="utf-8")
    next_phase = completed_phase + 1

    # Check if next phase exists in plan
    pattern = rf"## Phase {next_phase}[:\s]"
    if not re.search(pattern, master_plan, re.IGNORECASE):
        return False  # No more phases

    # Extract next phase spec (simple extraction)
    phase_pattern = rf"(## Phase {next_phase}[^\n]*\n)(.*?)(?=## Phase \d|$)"
    match = re.search(phase_pattern, master_plan, re.DOTALL | re.IGNORECASE)
    phase_spec = match.group(0) if match else f"Phase {next_phase} of project {slug}"

    # Update state
    state["status"] = f"phase_{next_phase}_planning"
    state["phase"] = next_phase
    state.pop("review_result", None)  # Clear stale review data
    _write_state_dict(project_dir, state)

    # Send to phase planner
    bus.send(Message.create(
        from_agent="runner",
        to_agent="phase_planner",
        type="task",
        payload={
            "phase": next_phase,
            "phase_spec": phase_spec[:3000],
            "idea_slug": slug,
        },
    ))
    return True


def _mark_complete(project_dir: pathlib.Path, state: dict, title: str) -> None:
    """Mark a project as complete in both state file and master_ideas.md."""
    state["status"] = "complete"
    state.pop("review_result", None)
    _write_state_dict(project_dir, state)

    # Mark in master_ideas.md
    mi_path = PROJECT_ROOT / "master_ideas.md"
    if mi_path.exists() and title:
        content = mi_path.read_text(encoding="utf-8")
        # Handle both [title] and title formats
        clean_title = title.strip("[]")
        updated = content.replace(f"- [ ] **{title}**", f"- [x] **{title}**")
        if updated == content:
            updated = content.replace(f"- [ ] **[{clean_title}]**", f"- [x] **[{clean_title}]**")
        if updated != content:
            mi_path.write_text(updated, encoding="utf-8")


def _write_state(project_dir: pathlib.Path, state: dict, new_status: str) -> None:
    """Update status in current_idea.json."""
    state["status"] = new_status
    state.pop("review_result", None)
    _write_state_dict(project_dir, state)


def _write_state_dict(project_dir: pathlib.Path, state: dict) -> None:
    """Write state dict to disk."""
    state_file = project_dir / "state" / "current_idea.json"
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _increment_retries(project_dir: pathlib.Path, phase_num: int) -> int:
    """Increment and return the retry count for a phase."""
    retries_file = project_dir / "state" / "phase_retries.json"
    try:
        data = json.loads(retries_file.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    key = f"phase_{phase_num}"
    data[key] = data.get(key, 0) + 1
    retries_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data[key]


def _reset_retries(project_dir: pathlib.Path, phase_num: int) -> None:
    """Reset retry counter for a phase."""
    retries_file = project_dir / "state" / "phase_retries.json"
    try:
        data = json.loads(retries_file.read_text(encoding="utf-8"))
        data.pop(f"phase_{phase_num}", None)
        retries_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def _append_polish(project_dir: pathlib.Path, phase_num: int, notes: str) -> None:
    """Save non-blocking review notes as deferred polish tasks."""
    path = PIPELINE_DIR / "state" / "plan_amendments.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    bullets = re.findall(r'^[-*]\s+(.+)$', notes, re.MULTILINE)
    if not bullets:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n### Phase {phase_num} Polish Items\n")
        for b in bullets:
            f.write(f"- [ ] (polish) {b}\n")


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

    # Reset abandoned 'processing' messages from previous run.
    # After a graceful shutdown, agents leave in-flight messages as 'processing'
    # in queue files.  Without resetting, has_active_work() returns True and
    # _rebuild_queues_from_state bails, preventing any work from being re-queued.
    stale = bus.reset_stale_processing()
    if stale:
        print(f"  🔄 Reset {stale} stale message(s) from previous run")

    if resume:
        # Resume always acts like --from-list: keep running until ALL projects
        # are done, not just the first queue drain.  This prevents the runner
        # from exiting when a message is in 'processing' state and the pending
        # queue looks empty to the health check.
        from_list = True
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

    # Start metrics collection
    run_metrics = RunMetrics.start(provider=provider, model=model)
    print(f"  Prompts:  {run_metrics.prompt_version}")

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

                # Compact queues periodically (every ~30 health checks ≈ 30 min)
                if _status_count > 0 and _status_count % 30 == 0:
                    compacted = bus.compact_all()
                    if compacted > 0:
                        print(f"  🧹 Compacted {compacted} stale messages from queues")

                # Check if all queues are empty AND all ideas done
                all_empty = bus.all_queues_empty()
                # Find the most recently updated project's current_idea.json
                idea_state = _get_active_idea_state(PIPELINE_DIR)

                # --- Per-session budget enforcement ---
                # If the active project has been running longer than
                # PROJECT_TIME_BUDGET, force-complete it so we move on.
                _active_slug = idea_state.get("_slug", "")
                _active_started = idea_state.get("started_at", "")
                if _active_slug and _active_started and idea_state.get("status", "") not in ("", "complete", "budget_exceeded"):
                    try:
                        _start = datetime.fromisoformat(_active_started)
                        _elapsed = (datetime.now(timezone.utc) - _start).total_seconds() / 60
                        if _elapsed > PROJECT_TIME_BUDGET:
                            _proj_file = PIPELINE_DIR / "projects" / _active_slug / "state" / "current_idea.json"
                            idea_state["status"] = "budget_exceeded"
                            idea_state["budget_note"] = f"Force-completed after {_elapsed:.0f} min (budget: {PROJECT_TIME_BUDGET} min)"
                            _proj_file.write_text(json.dumps(idea_state, indent=2), encoding="utf-8")
                            print(f"  💰 Budget exceeded for '{idea_state.get('title', _active_slug)}' ({_elapsed:.0f}m > {PROJECT_TIME_BUDGET}m) — skipping")
                    except Exception:
                        pass

                running_agents = sum(1 for s in health.values() if s == "running")

                # Print status line
                pending_total = sum(bus.queue_depth(r) for r in AGENT_ROLES)
                elapsed_m = (time.time() - start_time) / 60
                phase = idea_state.get("status", "?")
                title = idea_state.get("title", "")
                title_str = f" | [{title[:28]}]" if title else ""

                # --- Live task progress from tasks.md (not stale JSON) ---
                # The executor only writes tasks_done/tasks_total once at start.
                # We re-read the actual file every tick for live progress.
                tasks_done, tasks_total = 0, 0
                try:
                    slug = idea_state.get("_slug", "")
                    phase_num = idea_state.get("phase", 1)
                    if slug:
                        tasks_file = PIPELINE_DIR / "projects" / slug / f"phases/phase_{phase_num}/tasks.md"
                        if tasks_file.exists():
                            raw = tasks_file.read_text(encoding="utf-8")
                            # Scope to current phase only (some files have all phases)
                            from pipeline.agent_process import AgentProcess
                            scoped = AgentProcess._extract_phase_tasks(raw, phase_num)
                            tasks_total = len(re.findall(r'^- \[[ x]\]', scoped, re.MULTILINE))
                            tasks_done  = len(re.findall(r'^- \[x\]', scoped, re.MULTILINE | re.IGNORECASE))
                except Exception:
                    pass
                task_str = f" {tasks_done}/{tasks_total}✓" if tasks_total else ""

                status_line = _clean(
                    f"  [{elapsed_m:.0f}m] agents={running_agents}/{len(AGENT_ROLES)} "
                    f"pending={pending_total} phase={phase}{task_str}{title_str}"
                )
                # Always print on a new line — ’\r’ tricks break on cloud/Windows terminals.
                # Throttle to every 4 checks (~4 min) to keep output readable.
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
                        # Before seeding a NEW idea, re-scan project state files
                        # for any in-progress project whose queue message was lost
                        # (e.g. Ollama crash ate the message without nacking it).
                        # Re-queue them first — only move to new ideas when all
                        # existing projects are truly complete.
                        orphaned = _rebuild_queues_from_state(bus)
                        if orphaned:
                            print(f"  🔁 Re-queued {orphaned} orphaned project(s) — not seeding new ideas yet")
                        elif not seed_from_master_list(bus):
                            print(f"\n  ✓ All ideas processed — pipeline complete.")
                            break

                # --- Collect per-project metrics from state files ---
                try:
                    projects_dir = PIPELINE_DIR / "projects"
                    if projects_dir.exists():
                        for proj_dir in projects_dir.iterdir():
                            if not proj_dir.is_dir():
                                continue
                            slug = proj_dir.name
                            ci_path = proj_dir / "state" / "current_idea.json"
                            if ci_path.exists():
                                ci = json.loads(ci_path.read_text(encoding="utf-8"))
                                run_metrics.record_project_start(slug)
                                st = ci.get("status", "")
                                if st == "complete":
                                    # Read retry counts from phase_retries.json
                                    retries = 0
                                    pr_path = proj_dir / "state" / "phase_retries.json"
                                    if pr_path.exists():
                                        try:
                                            pr_data = json.loads(pr_path.read_text(encoding="utf-8"))
                                            retries = sum(v for v in pr_data.values() if isinstance(v, int))
                                        except Exception:
                                            pass
                                    run_metrics.record_project_complete(
                                        slug,
                                        phases=ci.get("phase", 0),
                                        retries=retries,
                                    )
                except Exception:
                    pass  # metrics are best-effort, never crash the runner

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

        # Finalize and save metrics report
        try:
            metrics_path = run_metrics.finish()
            metrics_report = metrics_path.parent / "report.md"
        except Exception as e:
            metrics_report = None
            print(f"  ⚠ Metrics save failed: {e}")

        signal.signal(signal.SIGINT, original_sigint)

        print("\n" + "=" * 60)
        print("  Pipeline stopped.")
        print(f"  Logs: .pipeline/logs/")
        print(f"  Output: .pipeline/workspace/")
        print(f"  Decisions: .pipeline/state/manager_decisions.md")
        if metrics_report and metrics_report.exists():
            print(f"  Run Report: {metrics_report.relative_to(PROJECT_ROOT)}")
            print(f"  Prompt Ver: {run_metrics.prompt_version}")
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
