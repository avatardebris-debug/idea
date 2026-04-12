"""
pipeline/agents/executor.py
Executor agent — implements coding tasks from the Phase Planner.

Receives: task list (phase_N/tasks.md path + content)
Produces: code files in .pipeline/workspace/, sends result to Validator
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from pipeline.agent_process import AgentProcess, AgentOutput
from pipeline.message_bus import Message


class ExecutorAgent(AgentProcess):
    role = "executor"
    max_steps = 30

    def handle(self, msg: Message) -> AgentOutput:
        phase_num = msg.payload.get("phase", 1)
        tasks_path = msg.payload.get("tasks_path", f"phases/phase_{phase_num}/tasks.md")

        # Read the task list
        tasks_content = self.read_state_file(tasks_path)
        if not tasks_content:
            return AgentOutput(
                success=False,
                error=f"No tasks file found at {tasks_path}",
            )

        # Read master plan for context
        master_plan = self.read_state_file("state/master_plan.md")

        # Build the task for the agent
        workspace = self.get_workspace_path()
        task_prompt = (
            f"You are implementing Phase {phase_num} of a project.\n\n"
            f"## Master Plan\n{master_plan[:2000]}\n\n"
            f"## Your Tasks\n{tasks_content}\n\n"
            f"## Instructions\n"
            f"1. Work through each unchecked task in order.\n"
            f"2. Write all code files to: {workspace}\n"
            f"3. After completing each task, update the tasks file at "
            f".pipeline/{tasks_path} marking it [x].\n"
            f"4. When ALL tasks are complete, say DONE and list every file you created.\n"
        )

        result = self.call_agent(task=task_prompt, verbose=False)

        # Determine what files were created/modified
        files_written = []
        if workspace.exists():
            files_written = [
                str(p.relative_to(workspace))
                for p in workspace.rglob("*")
                if p.is_file() and not p.name.startswith(".")
            ]

        # Send to Validator
        out_msg = Message.create(
            from_agent=self.role,
            to_agent="validator",
            type="task",
            payload={
                "phase": phase_num,
                "tasks_path": tasks_path,
                "workspace_path": str(workspace),
                "files_written": files_written,
                "validation_report_path": f"phases/phase_{phase_num}/validation_report.md",
            },
        )

        return AgentOutput(
            success=result.completed,
            answer=result.answer,
            outgoing=[out_msg],
            files_written=files_written,
            tokens_used=result.tokens_used,
            steps_used=result.steps_used,
        )


def main():
    """Entry point for subprocess execution."""
    import argparse
    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="ollama")
    parser.add_argument("--model", default="qwen3.5:35b")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [executor] %(message)s")

    agent = ExecutorAgent(provider=args.provider, model=args.model)
    agent.run_loop()


if __name__ == "__main__":
    main()
