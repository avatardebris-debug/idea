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
        idea_slug = msg.payload.get("idea_slug", self._current_slug)
        workspace_path = msg.payload.get("workspace_path", str(self.get_workspace_path()))
        files_written = msg.payload.get("files_written", [])
        tasks_path = msg.payload.get("tasks_path", f"phases/phase_{phase_num}/tasks.md")
        report_path = msg.payload.get(
            "validation_report_path",
            f"phases/phase_{phase_num}/validation_report.md",
        )
        report_full_path = self._project_path(report_path)

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
            f"3. BEFORE running tests, check for missing packages:\n"
            f"   - Scan import statements in the code files.\n"
            f"   - For each third-party import, test with `python -c 'import <pkg>'`.\n"
            f"   - If ModuleNotFoundError: run `pip install <pkg>` and retry.\n"
            f"   - Common mappings: bs4->beautifulsoup4, PIL->Pillow, yaml->pyyaml,\n"
            f"     cv2->opencv-python, dotenv->python-dotenv, sklearn->scikit-learn.\n"
            f"4. Run tests: `run_shell` with `cd {workspace_path} && python -m pytest -v` "
            f"(if test files exist).\n"
            f"   - If tests fail with ModuleNotFoundError, install the package and retry ONCE.\n"
            f"5. Run lint: `run_shell` with `cd {workspace_path} && python -m ruff check .` "
            f"(skip if ruff not installed).\n"
            f"6. Check each acceptance criterion from the task list.\n"
            f"7. Write your validation report to `{report_full_path}`.\n"
            f"8. End with a clear **Verdict: PASS** or **Verdict: FAIL**.\n"
            f"9. Say DONE.\n"
        )

        result = self.call_agent(task=task_prompt, verbose=False)

        # Determine verdict from the structured report ONLY
        report_content = self.read_state_file(report_path)
        is_pass = bool(report_content) and "Verdict: PASS" in report_content

        if is_pass:
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
                    "idea_slug": idea_slug,
                },
            )
        else:
            retry_count = msg.payload.get("retry_count", 0) + 1
            if retry_count >= 3:
                out_msg = Message.create(
                    from_agent=self.role,
                    to_agent="manager",
                    type="signal",
                    payload={
                        "signal": "PHASE_STUCK",
                        "phase": phase_num,
                        "reason": f"Validation failed after {retry_count} fix attempts",
                        "validation_report": report_content[:2000],
                        "idea_slug": idea_slug,
                    },
                )
            else:
                out_msg = Message.create(
                    from_agent=self.role,
                    to_agent="executor",
                    type="task",
                    payload={
                        "phase": phase_num,
                        "tasks_path": tasks_path,
                        "workspace_path": workspace_path,
                        "fix_required": True,
                        "retry_count": retry_count,
                        "validation_report": report_content[:3000],
                        "error_summary": f"Validation FAILED (attempt {retry_count}/3)",
                        "idea_slug": idea_slug,
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
