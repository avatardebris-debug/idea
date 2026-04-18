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
        idea_slug = msg.payload.get("idea_slug", self._current_slug)
        workspace_path = msg.payload.get("workspace_path", str(self.get_workspace_path()))
        files_written = msg.payload.get("files_written", [])
        validation_path = msg.payload.get("validation_report_path",
                                          f"phases/phase_{phase_num}/validation_report.md")
        review_path = msg.payload.get("review_path",
                                      f"phases/phase_{phase_num}/review.md")
        tasks_path = msg.payload.get("tasks_path",
                                     f"phases/phase_{phase_num}/tasks.md")
        review_full_path = self._project_path(review_path)

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
            f"3. Write your structured review to `{review_full_path}` using EXACTLY\n"
            f"   these section headings (in this order):\n\n"
            f"   ### What's Good\n"
            f"   (bullet list of things working correctly)\n\n"
            f"   ## Blocking Bugs\n"
            f"   (ONLY issues that will cause crashes, wrong output, or test failures)\n"
            f"   (reference file:line for each — if none write 'None')\n\n"
            f"   ## Non-Blocking Notes\n"
            f"   (style, naming, future improvements — do NOT list these as bugs)\n\n"
            f"   ## Verdict\n"
            f"   PASS or FAIL with one-line reason\n\n"
            f"4. A phase PASSES if '## Blocking Bugs' contains only 'None' or zero bullets.\n"
            f"5. Say DONE.\n"
        )

        result = self.call_agent(task=task_prompt, verbose=False)

        import re
        review_content = self.read_state_file(review_path)

        # Count only bullets under '## Blocking Bugs' — non-blocking notes are deferred work
        bugs_section = re.search(
            r'## Blocking Bugs.*?(?=## |$)', review_content, re.DOTALL | re.IGNORECASE
        )
        if bugs_section:
            section_text = bugs_section.group()
            if re.search(r'\bnone\b', section_text, re.IGNORECASE):
                blocking_count = 0
            else:
                blocking_count = len(re.findall(r'^[-*]\s+', section_text, re.MULTILINE))
        else:
            blocking_count = 0

        # Extract non-blocking notes to pass through for deferred scheduling
        non_blocking_section = re.search(
            r'## Non-Blocking Notes.*?(?=## |$)', review_content, re.DOTALL | re.IGNORECASE
        )
        non_blocking_notes = ""
        if non_blocking_section:
            raw = non_blocking_section.group().strip()
            # Only capture if there are actual bullet items (not just the heading)
            if re.search(r'^[-*]\s+', raw, re.MULTILINE):
                non_blocking_notes = raw

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
                "non_blocking_notes": non_blocking_notes[:1500],
                "review_content_preview": review_content[:1500],
                "idea_slug": idea_slug,
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
