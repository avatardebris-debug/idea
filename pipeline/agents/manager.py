"""
pipeline/agents/manager.py
Manager agent — orchestrator that routes all results and manages pipeline flow.

The ONLY agent that writes to other agents' queues.
Receives: results from Reviewer and Ideator
Produces: routing decisions, queue assignments, state updates
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from pipeline.agent_process import AgentProcess, AgentOutput
from pipeline.message_bus import Message


class ManagerAgent(AgentProcess):
    role = "manager"
    max_steps = 25
    temperature = 0.3   # coordination decisions should be consistent
    think = False       # routing logic is deterministic — CoT not needed

    # Emergency override threshold — if review mentions this many rework items
    REWORK_THRESHOLD = 0.75
    # Max reviewer-loop retries (validator loop is self-managed via progress tracking)
    MAX_PHASE_RETRIES = 12

    def handle(self, msg: Message) -> AgentOutput:
        source = msg.payload.get("source", msg.from_agent)
        outgoing = []

        if source == "ideator" or msg.from_agent == "ideator":
            outgoing = self._handle_ideator_result(msg)
        elif msg.from_agent == "reviewer":
            # Review routing is now handled deterministically by the runner's
            # _tick_project() function.  If the reviewer still sends us a
            # message (shouldn't happen post-migration), just log and drop it.
            self._log_decision(msg, [], note="Review routing now handled by runner — ignored")
        elif msg.type == "signal":
            outgoing = self._handle_pipeline_signal(msg)
        else:
            outgoing = self._handle_generic(msg)

        # Log the decision
        self._log_decision(msg, outgoing)

        return AgentOutput(
            success=True,
            answer=f"Processed {msg.type} from {msg.from_agent}, sent {len(outgoing)} messages",
            outgoing=outgoing,
        )

    # --- Ideator result handling ---

    def _handle_ideator_result(self, msg: Message) -> list[Message]:
        ideator_content = msg.payload.get("ideator_content_preview", "")
        ideator_path = msg.payload.get("ideator_output_path", "")

        # Use LLM to triage the ideas into separate destinations
        task_prompt = (
            f"You are the Manager triaging Ideator output into separate files.\n\n"
            f"## Ideator Output\n{ideator_content[:3000]}\n\n"
            f"## Current Master Ideas List\n"
            f"{self._read_master_ideas()[:2000]}\n\n"
            f"## Your Job\n"
            f"Categorize each idea into EXACTLY one of these 4 categories:\n"
            f"1. **ADD_TO_PLAN** — extends or improves what is currently being built\n"
            f"2. **REUSABLE_TOOL** — generic utility/library that could work across projects\n"
            f"3. **ADD_TO_BACKLOG** — a distinct new project idea for the future\n"
            f"4. **ARCHIVE** — interesting but not actionable right now\n\n"
            f"Then write EACH category to its own file (append, don't overwrite):\n\n"
            f"- **ADD_TO_PLAN** items → append to `.pipeline/state/plan_amendments.md`\n"
            f"  Format each as: `- [ ] <title>: <what to add and why>`\n\n"
            f"- **REUSABLE_TOOL** items → append to `.pipeline/state/reusable_tools.md`\n"
            f"  Format each as: `- <tool name>: <what it does, which agents/files it lives near>`\n\n"
            f"- **ADD_TO_BACKLOG** items → append to `master_ideas.md`\n"
            f"  Format each as: `- [ ] **<title>** — <one line description>`\n\n"
            f"- **ARCHIVE** items → append to `.pipeline/state/archived_ideas.md`\n"
            f"  Format each as: `- <title>: <reason archived>`\n\n"
            f"Write ALL four files even if a category is empty (just skip writing that one).\n"
            f"Say DONE when finished.\n"
        )

        result = self.call_agent(task=task_prompt, verbose=False)

        # No outgoing messages needed — the LLM call writes to files directly
        return []

    # --- Phase progression ---

    def _advance_phase(self, completed_phase: int, idea_slug: str = "") -> list[Message] | None:
        """Check if more phases exist and advance to next."""
        master_plan = self.read_state_file("state/master_plan.md")
        if not master_plan:
            return None

        next_phase_num = completed_phase + 1
        # Check if next phase exists in plan
        pattern = rf"## Phase {next_phase_num}[:\s]"
        if not re.search(pattern, master_plan, re.IGNORECASE):
            return None  # No more phases

        # Extract next phase spec
        from pipeline.agents.idea_planner import IdeaPlannerAgent
        temp = IdeaPlannerAgent.__new__(IdeaPlannerAgent)
        phase_spec = temp._extract_phase(master_plan, next_phase_num)

        # Update state
        self.write_json_state("state/current_phase.json", {
            "phase_num": next_phase_num,
            "status": "queued",
        })

        slug = idea_slug or self._current_slug
        return [Message.create(
            from_agent=self.role,
            to_agent="phase_planner",
            type="task",
            payload={
                "phase": next_phase_num,
                "phase_spec": phase_spec,
                "idea_slug": slug,
            },
        )]

    def _start_next_idea(self) -> list[Message]:
        """Pop the next unfinished idea from master_ideas.md.
        If master_ideas is empty, promote polish items from plan_amendments.md.
        """
        import re as _re2
        mi_path = pathlib.Path("master_ideas.md")
        if mi_path.exists():
            content = mi_path.read_text(encoding="utf-8")
            for line in content.split("\n"):
                match = _re2.match(r"- \[ \]\s+\*\*(.+?)\*\*\s*[—\u2013-]\s*(.*)", line)
                if match:
                    title = match.group(1).strip()
                    description = match.group(2).strip()
                    from pipeline.runner import _slugify
                    slug = _slugify(title)
                    return [Message.create(
                        from_agent=self.role,
                        to_agent="idea_planner",
                        type="task",
                        payload={"title": title, "idea": description, "idea_slug": slug},
                    )]

        # master_ideas.md is exhausted — promote polish items as a polish pass
        polish = self._start_next_polish_item()
        if polish:
            return polish

        return []  # Truly nothing left

    def _append_polish_items(self, phase_num: int, non_blocking_notes: str) -> None:
        """Save non-blocking review notes as deferred low-priority polish tasks."""
        import re as _re
        path = pathlib.Path(".pipeline/state/plan_amendments.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        # Extract just the bullet lines from the notes block
        bullets = _re.findall(r'^[-*]\s+(.+)$', non_blocking_notes, _re.MULTILINE)
        if not bullets:
            return
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n### Phase {phase_num} Polish Items\n")
            for b in bullets:
                f.write(f"- [ ] (polish) {b}\n")

    # --- Phase retry tracking ---

    def _retry_state_path(self) -> pathlib.Path:
        return self._project_dir / "state" / "phase_retries.json"

    def _get_phase_retries(self, phase_num: int) -> int:
        try:
            data = self.read_json_state("state/phase_retries.json")
            return data.get(f"phase_{phase_num}", 0)
        except Exception:
            return 0

    def _increment_phase_retries(self, phase_num: int) -> int:
        try:
            data = self.read_json_state("state/phase_retries.json")
        except Exception:
            data = {}
        key = f"phase_{phase_num}"
        data[key] = data.get(key, 0) + 1
        self.write_json_state("state/phase_retries.json", data)
        logger.info("[manager] Phase %d retry count: %d", phase_num, data[key])
        return data[key]

    def _reset_phase_retries(self, phase_num: int) -> None:
        try:
            data = self.read_json_state("state/phase_retries.json")
            data.pop(f"phase_{phase_num}", None)
            self.write_json_state("state/phase_retries.json", data)
        except Exception:
            pass

    def _count_tasks(self, phase_num: int) -> tuple[int, int]:
        """Return (done, total) task counts for the CURRENT phase only."""
        import re as _re
        raw = self.read_state_file(f"phases/phase_{phase_num}/tasks.md")
        if not raw:
            return 0, 0
        content = self._extract_phase_tasks(raw, phase_num)
        total = len(_re.findall(r'^- \[[ x]\]', content, _re.MULTILINE))
        done  = len(_re.findall(r'^- \[x\]',    content, _re.MULTILINE | _re.IGNORECASE))
        return done, total



    def _start_next_polish_item(self) -> list[Message]:
        """When all ideas are done, bundle unchecked polish items into a new task."""
        import re as _re
        path = pathlib.Path(".pipeline/state/plan_amendments.md")
        if not path.exists():
            return []

        content = path.read_text(encoding="utf-8")
        unchecked = _re.findall(r'^- \[ \] (.*)', content, _re.MULTILINE)
        if not unchecked:
            return []  # All polish done too

        # Bundle up to 5 polish items into one synthetic idea
        batch = unchecked[:5]
        batch_desc = "\n".join(f"- {item}" for item in batch)

        # Mark them as in-progress in the file so they aren't picked up again
        updated = content
        for item in batch:
            updated = updated.replace(f"- [ ] {item}", f"- [/] {item}", 1)
        path.write_text(updated, encoding="utf-8")

        self._log_decision(
            msg=Message.create(
                from_agent=self.role, to_agent=self.role,
                type="internal", payload={},
            ),
            outgoing=[],
            note=f"Promoting {len(batch)} polish items as synthetic idea",
        )

        return [Message.create(
            from_agent=self.role,
            to_agent="idea_planner",
            type="task",
            payload={
                "title": "Polish Pass",
                "idea": (
                    "Apply the following low-priority improvements identified during code review.\n"
                    "These are non-blocking quality improvements, not bug fixes:\n\n"
                    + batch_desc
                ),
            },
        )]

    def _mark_idea_complete(self) -> None:
        """Mark the current idea as done in both state file and master_ideas.md."""
        # --- Update current_idea.json (critical for _rebuild_queues_from_state) ---
        try:
            idea_state = self.read_json_state("state/current_idea.json")
            idea_state["status"] = "complete"
            self.write_json_state("state/current_idea.json", idea_state)
        except Exception:
            idea_state = {}

        title = idea_state.get("title", "")
        if not title:
            return

        mi_path = pathlib.Path("master_ideas.md")
        if not mi_path.exists():
            return

        content = mi_path.read_text(encoding="utf-8")
        # Replace [ ] with [x] for this idea
        updated = content.replace(f"- [ ] **{title}**", f"- [x] **{title}**")
        mi_path.write_text(updated, encoding="utf-8")

    def _read_master_ideas(self) -> str:
        mi_path = pathlib.Path("master_ideas.md")
        if mi_path.exists():
            return mi_path.read_text(encoding="utf-8")
        return "(no master ideas list)"

    # --- Signal handling ---

    def _handle_pipeline_signal(self, msg: Message) -> list[Message]:
        sig = msg.payload.get("signal", "")
        if sig == "PHASE_COMPLETE":
            phase = msg.payload.get("phase", 0)
            return self._advance_phase(phase) or []
        elif sig == "PHASE_STUCK":
            # Validation failed 3 times — log and skip phase, try next or stop
            phase = msg.payload.get("phase", 0)
            reason = msg.payload.get("reason", "unknown")
            self._log_decision(msg, [], note=f"PHASE_STUCK phase={phase}: {reason}")
            # Attempt to advance anyway (or stop if no more phases)
            next_msgs = self._advance_phase(phase)
            if next_msgs:
                return next_msgs
            else:
                self._mark_idea_complete()
                return self._start_next_idea()
        return []

    def _handle_generic(self, msg: Message) -> list[Message]:
        """Fallback handler for unexpected message types."""
        self._log_decision(msg, [], note="Unhandled message type — logged only")
        return []

    # --- Decision logging ---

    def _log_decision(
        self,
        msg: Message,
        outgoing: list[Message],
        note: str = "",
    ) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        destinations = [f"{m.to_agent}({m.type})" for m in outgoing]
        entry = (
            f"\n## {ts}\n"
            f"- **Input**: {msg.type} from {msg.from_agent} "
            f"(phase={msg.payload.get('phase', '?')})\n"
            f"- **Routed to**: {', '.join(destinations) if destinations else 'none'}\n"
        )
        if note:
            entry += f"- **Note**: {note}\n"

        decisions_path = pathlib.Path(".pipeline/state/manager_decisions.md")
        decisions_path.parent.mkdir(parents=True, exist_ok=True)
        with open(decisions_path, "a", encoding="utf-8") as f:
            f.write(entry)


def main():
    import argparse
    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="ollama")
    parser.add_argument("--model", default="qwen3.5:35b")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [manager] %(message)s")

    agent = ManagerAgent(provider=args.provider, model=args.model)
    agent.run_loop()


if __name__ == "__main__":
    main()
