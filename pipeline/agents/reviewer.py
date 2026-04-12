"""
pipeline/agents/reviewer.py
Reviewer agent — performs detailed line-by-line code review.

Receives: workspace + validation report after Validator passes
Produces: review.md, sends result to Manager
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from pipeline.agent_process import AgentProcess, AgentOutput
from pipeline.message_bus import Message


class ReviewerAgent(AgentProcess):
    role = "reviewer"
    max_steps = 20

    def handle(self, msg: Message) -> AgentOutput:
        phase_num = msg.payload.get("phase", 1)
        workspace_path = msg.payload.get("workspace_path", ".pipeline/workspace")
        files_written = msg.payload.get("files_written", [])
        validation_path = msg.payload.get("validation_report_path",
                                          f"phases/phase_{phase_num}/validation_report.md")
        review_path = msg.payload.get("review_path",
                                      f"phases/phase_{phase_num}/review.md")
        tasks_path = msg.payload.get("tasks_path",
                                     f"phases/phase_{phase_num}/tasks.md")

        # Read context
        tasks_content = self.read_state_file(tasks_path)
        validation_content = self.read_state_file(validation_path)

        task_prompt = (
            f"You are reviewing Phase {phase_num} code.\n\n"
            f"## Task Spec\n{tasks_content}\n\n"
            f"## Validation Report\n{validation_content[:2000]}\n\n"
            f"## Workspace\n"
            f"Code is in: {workspace_path}\n"
            f"Files: {', '.join(files_written) if files_written else '(use list_tree)'}\n\n"
            f"## Your Job\n"
            f"1. Read EVERY code file in {workspace_path}.\n"
            f"2. Review each file line by line.\n"
            f"3. Write your structured review to `.pipeline/{review_path}`.\n"
            f"4. Be specific — reference file:line for every issue.\n"
            f"5. Include a 'What\\'s Good' section — don't only criticize.\n"
            f"6. End with severity summary and overall assessment.\n"
            f"7. Say DONE.\n"
        )

        result = self.call_agent(task=task_prompt, verbose=False)

        # Read the review to extract severity counts
        # Count only lines in the "Bugs (blocking)" section,
        # not "non-blocking" mentions elsewhere
        import re
        review_content = self.read_state_file(review_path)
        bugs_section = re.search(
            r'## Bugs.*?(?=## |$)', review_content, re.DOTALL | re.IGNORECASE
        )
        if bugs_section:
            # Count list items in the bugs section
            blocking_count = len(re.findall(r'^[-*]\s+', bugs_section.group(), re.MULTILINE))
        else:
            blocking_count = 0

        # Always send to Manager
        out_msg = Message.create(
            from_agent=self.role,
            to_agent="manager",
            type="result",
            payload={
                "phase": phase_num,
                "review_path": review_path,
                "tasks_path": tasks_path,
                "workspace_path": workspace_path,
                "files_written": files_written,
                "blocking_bugs": blocking_count,
                "review_content_preview": review_content[:1500],
            },
        )

        return AgentOutput(
            success=True,
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

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [reviewer] %(message)s")

    agent = ReviewerAgent(provider=args.provider, model=args.model)
    agent.run_loop()


if __name__ == "__main__":
    main()
