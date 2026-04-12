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

    # Emergency override threshold — if review mentions this many rework items
    REWORK_THRESHOLD = 0.75

    def handle(self, msg: Message) -> AgentOutput:
        source = msg.payload.get("source", msg.from_agent)
        outgoing = []

        if source == "ideator" or msg.from_agent == "ideator":
            outgoing = self._handle_ideator_result(msg)
        elif msg.from_agent == "reviewer":
            outgoing = self._handle_review_result(msg)
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

    # --- Review result handling ---

    def _handle_review_result(self, msg: Message) -> list[Message]:
        phase_num = msg.payload.get("phase", 1)
        blocking_bugs = msg.payload.get("blocking_bugs", 0)
        review_content = msg.payload.get("review_content_preview", "")
        tasks_path = msg.payload.get("tasks_path", "")
        workspace_path = msg.payload.get("workspace_path", "")
        files_written = msg.payload.get("files_written", [])
        review_path = msg.payload.get("review_path", "")

        outgoing = []

        # Check for emergency rework
        rework_indicators = sum(1 for word in ["fundamental", "architectural",
                                                "completely wrong", "redesign",
                                                "start over", "rewrite"]
                                if word in review_content.lower())
        is_emergency = rework_indicators >= 3 or blocking_bugs > 5

        if is_emergency:
            # EMERGENCY REWORK — halt and reset
            outgoing.append(Message.create(
                from_agent=self.role,
                to_agent="executor",
                type="signal",
                payload={
                    "signal": "EMERGENCY_REWORK",
                    "phase": phase_num,
                    "reason": "Review indicates major architectural issues requiring rework",
                    "review_path": review_path,
                },
                priority=0,  # emergency priority
            ))
            # Re-queue to phase planner with rework context
            outgoing.append(Message.create(
                from_agent=self.role,
                to_agent="phase_planner",
                type="task",
                payload={
                    "phase": phase_num,
                    "phase_spec": f"REWORK REQUIRED — see review at .pipeline/{review_path}",
                    "is_rework": True,
                },
                priority=0,
            ))
        elif blocking_bugs > 0:
            # Send back to executor with fix instructions
            outgoing.append(Message.create(
                from_agent=self.role,
                to_agent="executor",
                type="task",
                payload={
                    "phase": phase_num,
                    "tasks_path": tasks_path,
                    "workspace_path": workspace_path,
                    "fix_required": True,
                    "review_path": review_path,
                    "blocking_bugs": blocking_bugs,
                    "fix_instructions": f"Fix {blocking_bugs} blocking bugs from review. "
                                       f"Read .pipeline/{review_path} for details.",
                },
            ))
        else:
            # Phase passes — check if more phases remain
            next_phase = self._advance_phase(phase_num)
            if next_phase:
                outgoing.extend(next_phase)
            else:
                # All phases done — mark idea complete
                self._mark_idea_complete()
                outgoing.extend(self._start_next_idea())

        # Only trigger Ideator when phase passes (not during emergency rework)
        if not is_emergency:
            outgoing.append(Message.create(
                from_agent=self.role,
                to_agent="ideator",
                type="task",
                payload={
                    "phase": phase_num,
                    "review_path": review_path,
                    "trigger": "post_review",
                },
            ))

        return outgoing

    # --- Ideator result handling ---

    def _handle_ideator_result(self, msg: Message) -> list[Message]:
        ideator_content = msg.payload.get("ideator_content_preview", "")
        ideator_path = msg.payload.get("ideator_output_path", "")

        # Use LLM to triage the ideas
        task_prompt = (
            f"You are the Manager triaging Ideator output.\n\n"
            f"## Ideator Output\n{ideator_content[:3000]}\n\n"
            f"## Current Master Ideas List\n"
            f"{self._read_master_ideas()[:2000]}\n\n"
            f"## Your Job\n"
            f"Categorize each idea:\n"
            f"1. **ADD_TO_PLAN** — should be added to current project's future phases\n"
            f"2. **ADD_TO_BACKLOG** — new idea for master_ideas.md\n"
            f"3. **ARCHIVE** — interesting but not actionable now\n\n"
            f"For each idea, write one line:\n"
            f"CATEGORY | idea title | brief reason\n\n"
            f"Then:\n"
            f"- Append any ADD_TO_BACKLOG items to `master_ideas.md`\n"
            f"- Log your decisions to `.pipeline/state/manager_decisions.md`\n"
            f"- Say DONE.\n"
        )

        result = self.call_agent(task=task_prompt, verbose=False)

        # No outgoing messages needed — the LLM call writes to files directly
        return []

    # --- Phase progression ---

    def _advance_phase(self, completed_phase: int) -> list[Message] | None:
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

        return [Message.create(
            from_agent=self.role,
            to_agent="phase_planner",
            type="task",
            payload={
                "phase": next_phase_num,
                "phase_spec": phase_spec,
            },
        )]

    def _start_next_idea(self) -> list[Message]:
        """Pop the next unfinished idea from master_ideas.md."""
        mi_path = pathlib.Path("master_ideas.md")
        if not mi_path.exists():
            return []

        content = mi_path.read_text(encoding="utf-8")
        # Find first line with [ ] (unchecked)
        for line in content.split("\n"):
            match = re.match(r"- \[ \]\s+\*\*(.+?)\*\*\s*[—–-]\s*(.*)", line)
            if match:
                title = match.group(1).strip()
                description = match.group(2).strip()
                return [Message.create(
                    from_agent=self.role,
                    to_agent="idea_planner",
                    type="task",
                    payload={
                        "title": title,
                        "idea": description,
                    },
                )]
        return []  # No more ideas

    def _mark_idea_complete(self) -> None:
        """Mark the current idea as done in master_ideas.md."""
        idea_state = self.read_json_state("state/current_idea.json")
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
