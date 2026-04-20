"""
pipeline/agents/phase_planner.py
Phase Planner agent — breaks a phase spec into concrete ordered tasks.

Receives: phase spec from Idea Planner (via Manager)
Produces: phase_N/tasks.md, sends first task batch to Executor
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from pipeline.agent_process import AgentProcess, AgentOutput
from pipeline.message_bus import Message


class PhasePlannerAgent(AgentProcess):
    role = "phase_planner"
    max_steps = 15
    temperature = 0.4   # slight creativity helps with edge-case task decomposition
    think = True        # reasoning here pays dividends for every downstream agent

    def handle(self, msg: Message) -> AgentOutput:
        phase_num = msg.payload.get("phase", 1)
        phase_spec = msg.payload.get("phase_spec", "")
        idea_slug = msg.payload.get("idea_slug", self._current_slug)
        tasks_path = f"phases/phase_{phase_num}/tasks.md"
        tasks_full_path = self._project_path(tasks_path)

        self._update_idea_status(f"phase_{phase_num}_planning")

        # Read master plan for full context
        master_plan = self.read_state_file("state/master_plan.md")

        # Read existing workspace to know what already exists
        workspace = self.get_workspace_path()

        task_prompt = (
            f"You are planning Phase {phase_num} of a project.\n\n"
            f"## Master Plan\n{master_plan[:3000]}\n\n"
            f"## This Phase's Spec\n{phase_spec}\n\n"
            f"## Instructions\n"
            f"1. Read the existing workspace with `list_tree` on {workspace} "
            f"to see what's already built.\n"
            f"2. Break this phase into 3-6 concrete, ordered coding tasks.\n"
            f"3. Write the task list to `{tasks_full_path}` using EXACTLY this format:\n\n"
            f"   ```\n"
            f"   # Phase {phase_num} Tasks\n\n"
            f"   - [ ] Task 1: <short title>\n"
            f"     - What: <what to build>\n"
            f"     - Files: <which files to create/modify>\n"
            f"     - Done when: <acceptance criteria — specific, testable>\n\n"
            f"   - [ ] Task 2: ...\n"
            f"   ```\n\n"
            f"   CRITICAL: Every task MUST start with `- [ ]`. "
            f"The executor marks tasks done with `- [x]` as it works.\n"
            f"   Do NOT use ## headings for tasks. Do NOT use ✅ or other symbols.\n"
            f"4. Say DONE.\n"
        )

        result = self.call_agent(task=task_prompt, verbose=False)

        # Write phase spec for reference
        self.write_state_file(f"phases/phase_{phase_num}/spec.md", phase_spec)

        # Update current phase state
        self.write_json_state("state/current_phase.json", {
            "phase_num": phase_num,
            "status": "planned",
            "tasks_path": tasks_path,
        })

        # Send to Executor
        out_msg = Message.create(
            from_agent=self.role,
            to_agent="executor",
            type="task",
            payload={
                "phase": phase_num,
                "tasks_path": tasks_path,
                "workspace_path": str(workspace),
                "idea_slug": idea_slug,
            },
        )

        return AgentOutput(
            success=result.completed,
            answer=result.answer,
            outgoing=[out_msg],
            tokens_used=result.tokens_used,
            steps_used=result.steps_used,
        )


def main():
    import argparse
    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="ollama")
    parser.add_argument("--model", default="qwen3.5:35b")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [phase_planner] %(message)s")

    agent = PhasePlannerAgent(provider=args.provider, model=args.model)
    agent.run_loop()


if __name__ == "__main__":
    main()
