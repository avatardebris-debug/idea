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
        idea_slug = msg.payload.get("idea_slug", self._current_slug)
        tasks_path = msg.payload.get("tasks_path", f"phases/phase_{phase_num}/tasks.md")
        fix_required = msg.payload.get("fix_required", False)
        fix_context = (msg.payload.get("validation_report", "")
                       or msg.payload.get("fix_instructions", ""))
        review_path = msg.payload.get("review_path", "")

        # Always read these upfront
        tasks_content = self.read_state_file(tasks_path)
        master_plan = self.read_state_file("state/master_plan.md")
        workspace = self.get_workspace_path()
        tasks_full_path = self._project_path(tasks_path)

        # Snapshot workspace BEFORE so we only report newly created files
        before_files = (
            {p for p in workspace.rglob("*") if p.is_file()}
            if workspace.exists() else set()
        )

        if fix_required:
            # Targeted fix prompt — agent knows exactly what failed
            review_content = self.read_state_file(review_path) if review_path else ""
            task_prompt = (
                f"You are fixing Phase {phase_num} code that failed validation/review.\n\n"
                f"## Workspace\n{workspace}\n\n"
                f"## What Failed\n{fix_context[:2000]}\n\n"
                + (f"## Review Details\n{review_content[:2000]}\n\n" if review_content else "")
                + "## Instructions\n"
                  "1. Read the failure report above carefully.\n"
                f"2. Use `list_tree` then `read_file` on each relevant source file.\n"
                  "3. Fix ONLY the blocking issues described. Don't rewrite working code.\n"
                f"4. Update tasks file at `{tasks_full_path}` if any task status changes.\n"
                  "5. Say DONE and list every file you changed.\n"
            )
        elif not tasks_content:
            return AgentOutput(
                success=False,
                error=f"No tasks file found at {tasks_full_path}",
            )
        else:
            task_prompt = (
                f"You are implementing Phase {phase_num} of a project.\n\n"
                f"## Master Plan\n{master_plan[:2000]}\n\n"
                f"## Your Tasks\n{tasks_content}\n\n"
                "## Instructions\n"
                "1. Work through each unchecked task in order.\n"
                f"2. Write all code files to: {workspace}\n"
                "3. After completing each task, update the tasks file at "
                f"`{tasks_full_path}` marking it [x].\n"
                "4. When ALL tasks are complete, say DONE and list every file you created.\n"
            )

        result = self.call_agent(task=task_prompt, verbose=False)

        # Only report files created/changed during THIS call
        after_files = (
            {p for p in workspace.rglob("*") if p.is_file()}
            if workspace.exists() else set()
        )
        new_files = after_files - before_files
        files_to_report = new_files if new_files else after_files
        files_written = [
            str(p.relative_to(workspace))
            for p in files_to_report
            if not p.name.startswith(".")
        ]

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
                "idea_slug": idea_slug,
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
