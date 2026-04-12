"""
pipeline/agents/validator.py
Validator/Tester agent — runs tests, lint, and acceptance checks.

Receives: workspace path + file list after Executor finishes
Produces: validation_report.md, sends result to Reviewer (on PASS) or back to Executor (on FAIL)
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from pipeline.agent_process import AgentProcess, AgentOutput
from pipeline.message_bus import Message


class ValidatorAgent(AgentProcess):
    role = "validator"
    max_steps = 20

    def handle(self, msg: Message) -> AgentOutput:
        phase_num = msg.payload.get("phase", 1)
        workspace_path = msg.payload.get("workspace_path", ".pipeline/workspace")
        files_written = msg.payload.get("files_written", [])
        tasks_path = msg.payload.get("tasks_path", f"phases/phase_{phase_num}/tasks.md")
        report_path = msg.payload.get(
            "validation_report_path",
            f"phases/phase_{phase_num}/validation_report.md",
        )

        # Read task list for acceptance criteria
        tasks_content = self.read_state_file(tasks_path)

        task_prompt = (
            f"You are validating Phase {phase_num} code output.\n\n"
            f"## Workspace\n"
            f"All code is in: {workspace_path}\n"
            f"Files written: {', '.join(files_written) if files_written else '(check workspace)'}\n\n"
            f"## Task List (for acceptance criteria)\n{tasks_content}\n\n"
            f"## Your Job\n"
            f"1. Use `list_tree` on {workspace_path} to see all files.\n"
            f"2. Read each code file.\n"
            f"3. Run tests: `run_shell` with `cd {workspace_path} && python -m pytest -v` "
            f"(if test files exist).\n"
            f"4. Run lint: `run_shell` with `cd {workspace_path} && python -m ruff check .` "
            f"(skip if ruff not installed).\n"
            f"5. Check each acceptance criterion from the task list.\n"
            f"6. Write your validation report to `.pipeline/{report_path}`.\n"
            f"7. End with a clear **Verdict: PASS** or **Verdict: FAIL**.\n"
            f"8. Say DONE.\n"
        )

        result = self.call_agent(task=task_prompt, verbose=False)

        # Determine verdict from the report
        report_content = self.read_state_file(report_path)
        is_pass = "Verdict: PASS" in report_content or "PASS" in result.answer.upper()

        if is_pass:
            # Send to Reviewer
            out_msg = Message.create(
                from_agent=self.role,
                to_agent="reviewer",
                type="task",
                payload={
                    "phase": phase_num,
                    "workspace_path": workspace_path,
                    "files_written": files_written,
                    "tasks_path": tasks_path,
                    "validation_report_path": report_path,
                    "review_path": f"phases/phase_{phase_num}/review.md",
                },
            )
        else:
            # Send back to Executor with failure context
            out_msg = Message.create(
                from_agent=self.role,
                to_agent="executor",
                type="task",
                payload={
                    "phase": phase_num,
                    "tasks_path": tasks_path,
                    "workspace_path": workspace_path,
                    "fix_required": True,
                    "validation_report": report_content[:3000],
                    "error_summary": "Validation FAILED — see report for details",
                },
            )

        return AgentOutput(
            success=is_pass,
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

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [validator] %(message)s")

    agent = ValidatorAgent(provider=args.provider, model=args.model)
    agent.run_loop()


if __name__ == "__main__":
    main()
