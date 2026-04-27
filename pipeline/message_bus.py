"""
pipeline/message_bus.py
File-based JSONL message queue for inter-agent communication.

Each agent has its own queue file at .pipeline/queues/{agent_name}.jsonl
Messages are append-only. Consumed messages are marked with status="done".

Thread/process safe via file locking (fcntl on Linux, msvcrt on Windows).
"""

from __future__ import annotations

import json
import os
import pathlib
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

# Always resolve .pipeline/ relative to the project root (this file's grandparent dir),
# NOT relative to wherever the runner is invoked from. This prevents duplicate
# .pipeline/ directories when the user starts the runner from different directories.
_PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
PIPELINE_DIR = _PROJECT_ROOT / ".pipeline"
QUEUES_DIR = PIPELINE_DIR / "queues"


# ---------------------------------------------------------------------------
# Message data model
# ---------------------------------------------------------------------------

@dataclass
class Message:
    """A single message in the pipeline queue."""
    msg_id: str = ""
    from_agent: str = ""
    to_agent: str = ""
    type: str = "task"           # task | result | signal | context
    priority: int = 1            # 1=normal, 0=emergency
    payload: dict = field(default_factory=dict)
    created_at: str = ""
    in_reply_to: str = ""
    status: str = "pending"      # pending | processing | done | failed

    def __post_init__(self):
        if not self.msg_id:
            self.msg_id = str(uuid.uuid4())[:12]
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Message":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})

    @classmethod
    def create(
        cls,
        from_agent: str,
        to_agent: str,
        type: str = "task",
        payload: dict | None = None,
        priority: int = 1,
        in_reply_to: str = "",
    ) -> "Message":
        return cls(
            from_agent=from_agent,
            to_agent=to_agent,
            type=type,
            payload=payload or {},
            priority=priority,
            in_reply_to=in_reply_to,
        )


# ---------------------------------------------------------------------------
# File lock context manager (cross-platform)
# ---------------------------------------------------------------------------

class _FileLock:
    """Simple file lock — uses msvcrt on Windows, fcntl on Unix."""

    def __init__(self, path: pathlib.Path):
        self.lock_path = path.with_suffix(path.suffix + ".lock")
        self._f = None

    def __enter__(self):
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._f = open(self.lock_path, "w")
        try:
            import msvcrt
            msvcrt.locking(self._f.fileno(), msvcrt.LK_LOCK, 1)
        except ImportError:
            import fcntl
            fcntl.flock(self._f.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *args):
        if self._f:
            try:
                import msvcrt
                msvcrt.locking(self._f.fileno(), msvcrt.LK_UNLCK, 1)
            except ImportError:
                import fcntl
                fcntl.flock(self._f.fileno(), fcntl.LOCK_UN)
            self._f.close()
            self._f = None


# ---------------------------------------------------------------------------
# MessageBus
# ---------------------------------------------------------------------------

class MessageBus:
    """File-backed message queue for the agent pipeline."""

    def __init__(self, base_dir: pathlib.Path | None = None):
        self.base_dir = base_dir or QUEUES_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _queue_path(self, agent_name: str) -> pathlib.Path:
        return self.base_dir / f"{agent_name}.jsonl"

    def send(self, msg: Message) -> None:
        """Append a message to the target agent's queue."""
        path = self._queue_path(msg.to_agent)
        with _FileLock(path):
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(msg.to_dict()) + "\n")

    def read_next(self, agent_name: str) -> Message | None:
        """Read the next pending message for an agent (FIFO, priority-aware).

        Returns None if no pending messages exist.
        Marks the message as 'processing' atomically.
        """
        path = self._queue_path(agent_name)
        if not path.exists():
            return None

        with _FileLock(path):
            lines = self._read_lines(path)
            messages = []
            for i, line in enumerate(lines):
                try:
                    d = json.loads(line)
                    if d.get("status") == "pending":
                        messages.append((i, d))
                except json.JSONDecodeError:
                    continue

            if not messages:
                return None

            # Sort by priority (0=emergency first), then by creation time
            messages.sort(key=lambda x: (x[1].get("priority", 1), x[1].get("created_at", "")))

            idx, chosen = messages[0]
            chosen["status"] = "processing"
            lines[idx] = json.dumps(chosen)
            self._write_lines(path, lines)

            return Message.from_dict(chosen)

    def ack(self, msg: Message) -> None:
        """Mark a message as done."""
        self._update_status(msg.to_agent, msg.msg_id, "done")

    def nack(self, msg: Message) -> None:
        """Mark a message as failed — it can be retried."""
        self._update_status(msg.to_agent, msg.msg_id, "pending")

    def fail(self, msg: Message) -> None:
        """Mark a message as permanently failed."""
        self._update_status(msg.to_agent, msg.msg_id, "failed")

    def peek(self, agent_name: str) -> list[Message]:
        """Return all pending messages without consuming them."""
        path = self._queue_path(agent_name)
        if not path.exists():
            return []

        pending = []
        with _FileLock(path):
            for line in self._read_lines(path):
                try:
                    d = json.loads(line)
                    if d.get("status") == "pending":
                        pending.append(Message.from_dict(d))
                except json.JSONDecodeError:
                    continue
        return pending

    def queue_depth(self, agent_name: str) -> int:
        """Return count of pending messages for an agent."""
        return len(self.peek(agent_name))

    def all_queues_empty(self, exclude: list[str] | None = None) -> bool:
        """Check if all agent queues have no PENDING messages.

        NOTE: does NOT count messages currently being processed (status='processing').
        Use has_active_work() to include in-flight messages.
        """
        exclude = set(exclude or [])
        for path in self.base_dir.glob("*.jsonl"):
            agent = path.stem
            if agent in exclude:
                continue
            if self.queue_depth(agent) > 0:
                return False
        return True

    def has_active_work(self) -> bool:
        """Return True if any queue has pending OR processing messages.

        Use this to decide whether to seed a new idea — if anything is
        still in-flight, don't start another idea yet.
        """
        for path in self.base_dir.glob("*.jsonl"):
            try:
                with _FileLock(path):
                    for line in self._read_lines(path):
                        try:
                            d = json.loads(line)
                            if d.get("status") in ("pending", "processing"):
                                return True
                        except json.JSONDecodeError:
                            continue
            except Exception:
                continue
        return False

    def send_signal(
        self,
        from_agent: str,
        to_agent: str,
        signal: str,
        payload: dict | None = None,
        priority: int = 1,
    ) -> None:
        """Send a signal message (PHASE_COMPLETE, EMERGENCY_REWORK, etc.)."""
        msg = Message.create(
            from_agent=from_agent,
            to_agent=to_agent,
            type="signal",
            payload={"signal": signal, **(payload or {})},
            priority=priority,
        )
        self.send(msg)

    def clear_queue(self, agent_name: str) -> int:
        """Remove all messages from an agent's queue. Returns count removed."""
        path = self._queue_path(agent_name)
        if not path.exists():
            return 0
        with _FileLock(path):
            lines = self._read_lines(path)
            count = len(lines)
            self._write_lines(path, [])
            return count

    def compact(self, agent_name: str) -> int:
        """Remove all 'done' and 'failed' messages from a queue file.

        Keeps only 'pending' and 'processing' messages.
        Called periodically by the runner to prevent queue files growing forever.
        Returns the number of messages removed.
        """
        path = self._queue_path(agent_name)
        if not path.exists():
            return 0
        with _FileLock(path):
            lines = self._read_lines(path)
            kept = []
            removed = 0
            for line in lines:
                try:
                    d = json.loads(line)
                    if d.get("status") in ("pending", "processing"):
                        kept.append(line)
                    else:
                        removed += 1
                except json.JSONDecodeError:
                    removed += 1  # malformed lines get cleaned up too
            if removed > 0:
                self._write_lines(path, kept)
            return removed

    def compact_all(self) -> int:
        """Compact all agent queues. Returns total messages removed."""
        total = 0
        if QUEUES_DIR.exists():
            for qf in QUEUES_DIR.glob("*.jsonl"):
                agent = qf.stem
                total += self.compact(agent)
        return total

    def reset_stale_processing(self) -> int:
        """Reset all 'processing' messages back to 'pending'.

        Called at startup to recover messages abandoned by agents that were
        killed mid-flight.  Without this, has_active_work() returns True
        even though no agents are running, blocking queue rebuilds.

        Returns the number of messages reset.
        """
        total = 0
        if not QUEUES_DIR.exists():
            return 0
        for qf in QUEUES_DIR.glob("*.jsonl"):
            with _FileLock(qf):
                lines = self._read_lines(qf)
                changed = False
                for i, line in enumerate(lines):
                    try:
                        d = json.loads(line)
                        if d.get("status") == "processing":
                            d["status"] = "pending"
                            lines[i] = json.dumps(d)
                            changed = True
                            total += 1
                    except json.JSONDecodeError:
                        continue
                if changed:
                    self._write_lines(qf, lines)
        return total

    # --- Internal helpers ---

    def _update_status(self, agent_name: str, msg_id: str, new_status: str) -> None:
        path = self._queue_path(agent_name)
        if not path.exists():
            return
        with _FileLock(path):
            lines = self._read_lines(path)
            for i, line in enumerate(lines):
                try:
                    d = json.loads(line)
                    if d.get("msg_id") == msg_id:
                        d["status"] = new_status
                        lines[i] = json.dumps(d)
                        break
                except json.JSONDecodeError:
                    continue
            self._write_lines(path, lines)

    @staticmethod
    def _read_lines(path: pathlib.Path) -> list[str]:
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            return [l.strip() for l in f.readlines() if l.strip()]

    @staticmethod
    def _write_lines(path: pathlib.Path, lines: list[str]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
