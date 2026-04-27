"""
pipeline/agents/idea_planner.py
Idea Planner agent — turns a raw idea into a multi-phase master plan.

Receives: idea description (from user or master_ideas.md)
Produces: master_plan.md, sends Phase 1 spec to Phase Planner
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


class IdeaPlannerAgent(AgentProcess):
    role = "idea_planner"
    max_steps = 15
    temperature = 0.5   # needs to reason about architecture — moderate creativity
    think = True        # reasoning helps produce better multi-phase project structures

    def handle(self, msg: Message) -> AgentOutput:
        idea_description = msg.payload.get("idea", "")
        idea_title = msg.payload.get("title", "Untitled Idea")
        idea_slug = msg.payload.get("idea_slug", self._current_slug)

        master_plan_path = self._project_path("state/master_plan.md")

        task_prompt = (
            f"You are the Idea Planner. Create a multi-phase implementation plan.\n\n"
            f"## Idea\n**{idea_title}**\n\n{idea_description}\n\n"
            f"## Instructions\n"
            f"1. Analyze the idea and identify the core deliverable.\n"
            f"2. Break it into exactly 3 phases by default. Phase 1 must be the smallest\n"
            f"   useful thing (MVP). Only use 4-6 phases if the idea genuinely requires it\n"
            f"   (e.g. multiple distinct subsystems that can't ship together).\n"
            f"3. Write the master plan to `{master_plan_path}`.\n"
            f"4. Each phase needs: description, deliverable, dependencies, success criteria.\n"
            f"5. Include architecture notes and risks.\n"
            f"6. Say DONE.\n"
        )

        result = self.call_agent(task=task_prompt, verbose=False)

        # Read the master plan to extract Phase 1
        master_plan = self.read_state_file("state/master_plan.md")
        phase_1_spec = self._extract_phase(master_plan, 1)


        # Save current idea state
        self.write_json_state("state/current_idea.json", {
            "title": idea_title,
            "description": idea_description[:500],
            "status": "planning",
            "phase": 1,
            "total_phases": self._count_phases(master_plan),
            "started_at": datetime.now(timezone.utc).isoformat(),
        })

        # Send Phase 1 to Phase Planner
        out_msg = Message.create(
            from_agent=self.role,
            to_agent="phase_planner",
            type="task",
            payload={
                "phase": 1,
                "phase_spec": phase_1_spec,
                "idea_slug": idea_slug,
                "idea_title": idea_title,
            },
        )

        return AgentOutput(
            success=result.completed,
            answer=result.answer,
            outgoing=[out_msg],
            tokens_used=result.tokens_used,
            steps_used=result.steps_used,
        )

    def _extract_phase(self, master_plan: str, phase_num: int) -> str:
        """Extract a specific phase section from the master plan."""
        if not master_plan:
            return f"Phase {phase_num} — (no plan available)"

        # Try to find the phase section using common heading patterns
        patterns = [
            rf"(## Phase {phase_num}[:\s].*?)(?=## Phase \d|## Architecture|## Risks|$)",
            rf"(### Phase {phase_num}[:\s].*?)(?=### Phase \d|### Architecture|### Risks|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, master_plan, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return f"Phase {phase_num} — see master plan for details"

    def _count_phases(self, master_plan: str) -> int:
        """Count how many phases are in the master plan."""
        matches = re.findall(r"##\s+Phase\s+\d+", master_plan, re.IGNORECASE)
        return len(matches) if matches else 1


def main():
    import argparse
    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="ollama")
    parser.add_argument("--model", default="qwen3.5:35b")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [idea_planner] %(message)s")

    agent = IdeaPlannerAgent(provider=args.provider, model=args.model)
    agent.run_loop()


if __name__ == "__main__":
    main()
