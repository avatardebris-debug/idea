"""
pipeline/agent_process.py
Base class for all pipeline agents.

Each agent runs as a subprocess, polling its queue and processing messages.
The base class handles:
  - Queue polling
  - System prompt construction (from prompts/ markdown files)
  - Calling the core ReAct loop (agent.py::run_agent)
  - Sending results downstream
  - Logging
  - Graceful shutdown
"""

from __future__ import annotations

import json
import logging
import os
import pathlib
import signal
import sys
import time
from dataclasses import dataclass, field
from typing import Any

# Ensure project root is on path
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.message_bus import MessageBus, Message

logger = logging.getLogger(__name__)

PIPELINE_DIR = pathlib.Path(".pipeline")
PROMPTS_DIR = pathlib.Path(__file__).parent / "prompts"
LOGS_DIR = PIPELINE_DIR / "logs"


# ---------------------------------------------------------------------------
# Agent result from a single handle() call
# ---------------------------------------------------------------------------

@dataclass
class AgentOutput:
    """Structured output from one agent processing cycle."""
    success: bool = True
    answer: str = ""
    outgoing: list[Message] = field(default_factory=list)
    files_written: list[str] = field(default_factory=list)
    error: str = ""
    tokens_used: int = 0
    steps_used: int = 0


# ---------------------------------------------------------------------------
# Base agent process
# ---------------------------------------------------------------------------

class AgentProcess:
    """
    Base class for all pipeline agents.

    Subclasses must implement:
      - role (class attribute): str — the agent's role name
      - handle(msg: Message) -> AgentOutput — process one message

    Optionally override:
      - build_context(msg) — add extra context to the system prompt
      - max_steps — how many ReAct steps this agent gets
    """

    role: str = "base"
    max_steps: int = 20
    poll_interval: float = 2.0   # seconds between queue checks

    def __init__(
        self,
        provider: str = "ollama",
        model: str = "qwen3.5:35b",
        bus: MessageBus | None = None,
    ):
        self.provider = provider
        self.model = model
        self.bus = bus or MessageBus()
        self._stop_requested = False
        self._setup_logging()
        self._setup_signal_handlers()

    # --- Lifecycle ---

    def run_loop(self) -> None:
        """Main loop: poll queue → handle → send results. Runs until stopped."""
        # Recover any messages stuck in 'processing' state from a previous crash
        self._recover_processing_messages()

        logger.info("[%s] Starting agent loop (provider=%s, model=%s)",
                    self.role, self.provider, self.model)

        while not self._stop_requested:
            msg = self.bus.read_next(self.role)

            if msg is None:
                time.sleep(self.poll_interval)
                continue

            # Handle signals specially
            if msg.type == "signal":
                self._handle_signal(msg)
                self.bus.ack(msg)
                continue

            logger.info("[%s] Processing message %s from %s (type=%s)",
                        self.role, msg.msg_id, msg.from_agent, msg.type)

            try:
                output = self.handle(msg)

                # Send outgoing messages
                for out_msg in output.outgoing:
                    self.bus.send(out_msg)
                    logger.info("[%s] Sent %s to %s",
                                self.role, out_msg.type, out_msg.to_agent)

                self.bus.ack(msg)

                logger.info("[%s] Completed message %s (success=%s, tokens=%d, steps=%d)",
                            self.role, msg.msg_id, output.success,
                            output.tokens_used, output.steps_used)

            except Exception as e:
                logger.error("[%s] Failed processing message %s: %s",
                             self.role, msg.msg_id, e, exc_info=True)
                self.bus.nack(msg)
                time.sleep(5)  # back off on failure

        logger.info("[%s] Shutting down", self.role)

    def stop(self) -> None:
        """Request graceful shutdown."""
        self._stop_requested = True

    # --- Core: subclasses implement these ---

    def handle(self, msg: Message) -> AgentOutput:
        """Process a single message. Must be overridden by subclasses."""
        raise NotImplementedError(f"{self.role} must implement handle()")

    def build_context(self, msg: Message) -> str:
        """Optional extra context injected into the system prompt.

        Override to add phase-specific state, file listings, etc.
        """
        return ""

    # --- Prompt construction ---

    def load_system_prompt(self) -> str:
        """Load the agent's system prompt from its markdown template."""
        prompt_path = PROMPTS_DIR / f"{self.role}.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        logger.warning("[%s] No prompt file found at %s", self.role, prompt_path)
        return f"You are the {self.role} agent in an idea development pipeline."

    def build_full_prompt(self, msg: Message) -> str:
        """Construct the complete task prompt for the ReAct loop."""
        base_prompt = self.load_system_prompt()
        context = self.build_context(msg)

        sections = [base_prompt]

        if context:
            sections.append(f"\n## Current Context\n{context}")

        if msg.payload:
            sections.append(f"\n## Task Payload\n```json\n{json.dumps(msg.payload, indent=2)}\n```")

        return "\n\n".join(sections)

    # --- Helper: call the core ReAct agent ---

    def call_agent(
        self,
        task: str,
        system_prompt_addon: str = "",
        max_steps: int | None = None,
        verbose: bool = False,
    ) -> "AgentResult":
        """Run the core ReAct loop from agent.py."""
        from agent import run_agent
        return run_agent(
            task=task,
            provider=self.provider,
            model=self.model,
            max_steps=max_steps or self.max_steps,
            system_prompt_addon=system_prompt_addon,
            verbose=verbose,
        )

    # --- Helper: read pipeline state files ---

    def read_state_file(self, relative_path: str) -> str:
        """Read a file from .pipeline/ state directory."""
        path = PIPELINE_DIR / relative_path
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def write_state_file(self, relative_path: str, content: str) -> None:
        """Write a file to .pipeline/ state directory."""
        path = PIPELINE_DIR / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def read_json_state(self, relative_path: str) -> dict:
        """Read a JSON state file."""
        content = self.read_state_file(relative_path)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {}
        return {}

    def write_json_state(self, relative_path: str, data: dict) -> None:
        """Write a JSON state file."""
        self.write_state_file(relative_path, json.dumps(data, indent=2))

    def get_current_phase(self) -> dict:
        """Read current phase state."""
        return self.read_json_state("state/current_phase.json")

    def get_workspace_path(self) -> pathlib.Path:
        """Return the workspace path where code output goes."""
        ws = PIPELINE_DIR / "workspace"
        ws.mkdir(parents=True, exist_ok=True)
        return ws

    # --- Signal handling ---

    def _handle_signal(self, msg: Message) -> None:
        """Process signal messages."""
        sig = msg.payload.get("signal", "")
        logger.info("[%s] Received signal: %s from %s", self.role, sig, msg.from_agent)

        if sig == "SHUTDOWN":
            self.stop()
        elif sig == "PAUSE":
            logger.info("[%s] Paused — waiting for RESUME", self.role)
            while not self._stop_requested:
                resume = self.bus.read_next(self.role)
                if resume and resume.type == "signal" and resume.payload.get("signal") == "RESUME":
                    self.bus.ack(resume)
                    logger.info("[%s] Resumed", self.role)
                    break
                if resume:
                    self.bus.nack(resume)  # put non-resume messages back
                time.sleep(1)

    def _setup_signal_handlers(self) -> None:
        """Handle OS-level signals for graceful shutdown."""
        def _handler(signum, frame):
            logger.info("[%s] Received signal %s, requesting stop", self.role, signum)
            self._stop_requested = True

        try:
            signal.signal(signal.SIGINT, _handler)
            signal.signal(signal.SIGTERM, _handler)
        except (OSError, ValueError):
            pass  # can't set signal handlers in non-main threads

    def _recover_processing_messages(self) -> None:
        """On startup, reset any 'processing' messages back to 'pending'.

        If a subprocess crashed mid-handle(), those messages are stuck in
        'processing' and invisible to read_next(). This makes them retryable.
        """
        import json as _json
        path = self.bus._queue_path(self.role)
        if not path.exists():
            return
        from pipeline.message_bus import _FileLock
        with _FileLock(path):
            lines = self.bus._read_lines(path)
            changed = False
            for i, line in enumerate(lines):
                try:
                    d = _json.loads(line)
                    if d.get("status") == "processing":
                        d["status"] = "pending"
                        lines[i] = _json.dumps(d)
                        changed = True
                        logger.warning("[%s] Recovered stuck message %s",
                                       self.role, d.get("msg_id", "?"))
                except _json.JSONDecodeError:
                    continue
            if changed:
                self.bus._write_lines(path, lines)

    def _setup_logging(self) -> None:
        """Configure per-agent log file."""
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOGS_DIR / f"{self.role}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
        ))

        agent_logger = logging.getLogger(f"pipeline.{self.role}")
        agent_logger.addHandler(file_handler)
        agent_logger.setLevel(logging.INFO)

        # Also add to the module logger
        logger.addHandler(file_handler)
