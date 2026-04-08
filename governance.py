"""
governance.py
Governance layer — loads the constitution, runs the governance pipeline,
and provides the affirmation system.

Integrates AutoHarness's ToolGovernancePipeline when available, with a
standalone fallback for environments without AutoHarness installed.
"""

from __future__ import annotations

import json
import logging
import pathlib
import re
import time
from dataclasses import dataclass, field
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constitution loader
# ---------------------------------------------------------------------------

CONSTITUTION_PATH = pathlib.Path("constitution.yaml")


@dataclass
class GovernanceDecision:
    """Result of evaluating a tool call against the constitution."""
    action: str        # "allow" | "deny" | "ask"
    reason: str = ""
    risk_level: str = "low"
    source: str = "governance"


def load_constitution(path: str | pathlib.Path | None = None) -> dict[str, Any]:
    """Load the constitution YAML and return the full config dict.

    Falls back to defaults if the file doesn't exist.
    """
    p = pathlib.Path(path) if path else CONSTITUTION_PATH
    if not p.exists():
        logger.warning("Constitution file not found at %s — using defaults", p)
        return _default_constitution()

    try:
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        logger.info("Constitution loaded from %s", p)
        return data or {}
    except Exception as e:
        logger.error("Failed to load constitution: %s — using defaults", e)
        return _default_constitution()


def _default_constitution() -> dict[str, Any]:
    """Minimal built-in constitution when no YAML file is found."""
    return {
        "identity": {"name": "default-agent", "description": "Ungoverned agent"},
        "rules": [],
        "permissions": {
            "defaults": {"policy": "allow"},
            "tools": {
                "run_shell": {
                    "policy": "restricted",
                    "deny_patterns": [r"rm\s+-rf\s+/", r"mkfs\."],
                    "require_confirmation": True,
                },
                "delete_file": {"policy": "restricted", "require_confirmation": True},
            },
        },
        "core_imperatives": {},
        "negative_imperatives": {},
        "internal_drives": {},
        "affirmation": {"enabled": False},
        "amygdala": {"enabled": False},
    }


# ---------------------------------------------------------------------------
# Governance Gate (standalone — no AutoHarness dependency)
# ---------------------------------------------------------------------------


class GovernanceGate:
    """Pre-execution governance gate for agent tool calls.

    Evaluates each tool call against the constitution's permissions,
    deny patterns, and negative imperatives before allowing execution.

    Can optionally delegate to AutoHarness's ToolGovernancePipeline
    when installed, but works standalone with pattern-based rules.
    """

    def __init__(self, constitution: dict[str, Any] | None = None):
        self.constitution = constitution or load_constitution()
        self._pipeline = None
        self._task_count = 0
        self._blocked_count = 0
        self._allowed_count = 0
        self._audit_log: list[dict[str, Any]] = []
        self._start_time = time.time()

        # Try to initialize AutoHarness pipeline
        self._try_init_autoharness()

        # Build standalone deny patterns from constitution
        self._deny_patterns = self._build_deny_patterns()

    def _try_init_autoharness(self) -> None:
        """Try to use AutoHarness for governance. Fall back to standalone if unavailable."""
        try:
            import sys
            # Add AutoHarness to path if it's in the project
            ah_path = pathlib.Path("AutoHarness-main")
            if ah_path.exists() and str(ah_path) not in sys.path:
                sys.path.insert(0, str(ah_path))

            from autoharness.core.constitution import Constitution
            from autoharness.core.pipeline import ToolGovernancePipeline
            from autoharness.core.types import ToolCall

            # Load constitution through AutoHarness (it handles the standard fields)
            ah_constitution = Constitution.from_dict(self.constitution)
            self._pipeline = ToolGovernancePipeline(ah_constitution, mode="core")
            self._ToolCall = ToolCall
            logger.info("AutoHarness governance pipeline initialized (core mode)")
        except Exception as e:
            logger.info("AutoHarness not available (%s) — using standalone governance", e)
            self._pipeline = None

    def _build_deny_patterns(self) -> dict[str, list[re.Pattern]]:
        """Extract and compile deny patterns from constitution permissions."""
        patterns: dict[str, list[re.Pattern]] = {}
        tools_config = self.constitution.get("permissions", {}).get("tools", {})

        if isinstance(tools_config, dict):
            for tool_name, tool_cfg in tools_config.items():
                if isinstance(tool_cfg, dict):
                    raw_patterns = tool_cfg.get("deny_patterns", [])
                    compiled = []
                    for p in raw_patterns:
                        try:
                            compiled.append(re.compile(p, re.IGNORECASE))
                        except re.error as e:
                            logger.warning("Invalid deny pattern '%s' for %s: %s", p, tool_name, e)
                    if compiled:
                        patterns[tool_name] = compiled

        return patterns

    def evaluate(self, tool_name: str, tool_args: dict[str, Any]) -> GovernanceDecision:
        """Evaluate a tool call against the constitution.

        Order of evaluation:
        1. Our deny-pattern checks ALWAYS run first (fast, reflexive — like the amygdala)
        2. AutoHarness pipeline runs second if available (for additional governance)
        3. Default: allow

        Returns a GovernanceDecision with action = allow/deny/ask.
        """
        # Step 1: Pattern-based deny check (always runs — our "amygdala reflex")
        pattern_decision = self._check_deny_patterns(tool_name, tool_args)
        if pattern_decision is not None:
            self._log_decision(tool_name, tool_args, pattern_decision)
            return pattern_decision

        # Step 2: AutoHarness pipeline (if available)
        if self._pipeline is not None:
            try:
                tc = self._ToolCall(
                    tool_name=tool_name,
                    tool_input=tool_args,
                    metadata={"provider": "agent.py"},
                )
                decision = self._pipeline.evaluate(tc)
                if decision.action == "deny":
                    result = GovernanceDecision(
                        action="deny",
                        reason=decision.reason or "Blocked by AutoHarness",
                        risk_level=str(getattr(decision.risk_level, "value", "high"))
                            if hasattr(decision, "risk_level") and decision.risk_level else "high",
                        source="autoharness",
                    )
                    self._log_decision(tool_name, tool_args, result)
                    return result
            except Exception as e:
                logger.warning("AutoHarness evaluation failed: %s", e)

        # Step 3: Check if tool requires confirmation
        tools_config = self.constitution.get("permissions", {}).get("tools", {})
        if isinstance(tools_config, dict):
            tool_cfg = tools_config.get(tool_name, {})
            if isinstance(tool_cfg, dict) and tool_cfg.get("require_confirmation"):
                result = GovernanceDecision(
                    action="allow",
                    reason="Tool requires confirmation (auto-allowed in Phase 1)",
                    risk_level="medium",
                    source="governance",
                )
                self._log_decision(tool_name, tool_args, result)
                return result

        # Default: allow
        result = GovernanceDecision(
            action="allow",
            reason="No restrictions matched",
            risk_level="low",
            source="governance",
        )
        self._log_decision(tool_name, tool_args, result)
        return result

    def _check_deny_patterns(self, tool_name: str, tool_args: dict[str, Any]) -> GovernanceDecision | None:
        """Check tool call against deny patterns. Returns decision if blocked, None otherwise."""
        if tool_name not in self._deny_patterns:
            return None

        # Match each arg value individually against patterns
        for arg_name, arg_value in tool_args.items():
            arg_str = str(arg_value)
            for pattern in self._deny_patterns[tool_name]:
                if pattern.search(arg_str):
                    return GovernanceDecision(
                        action="deny",
                        reason=f"Blocked by deny pattern: {pattern.pattern} (matched in '{arg_name}')",
                        risk_level="high",
                        source="amygdala",
                    )
        return None




    def _log_decision(self, tool_name: str, tool_args: dict, decision: GovernanceDecision) -> None:
        """Record the decision to the audit log."""
        if decision.action == "deny":
            self._blocked_count += 1
        else:
            self._allowed_count += 1

        entry = {
            "timestamp": time.time(),
            "tool_name": tool_name,
            "action": decision.action,
            "reason": decision.reason,
            "risk_level": decision.risk_level,
            "source": decision.source,
        }
        self._audit_log.append(entry)

        # Write to audit file
        audit_path = self.constitution.get("audit", {}).get("output", ".agent/audit.jsonl")
        try:
            p = pathlib.Path(audit_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning("Failed to write audit log: %s", e)

    @property
    def stats(self) -> dict[str, Any]:
        """Return governance statistics."""
        return {
            "allowed": self._allowed_count,
            "blocked": self._blocked_count,
            "total": self._allowed_count + self._blocked_count,
            "uptime_seconds": time.time() - self._start_time,
        }


# ---------------------------------------------------------------------------
# Affirmation System
# ---------------------------------------------------------------------------


class AffirmationSystem:
    """Dynamic context injection system.

    Periodically refreshes constitution values, affirmation statements,
    and motivational context into the agent's system prompt.

    This is the functional equivalent of human self-talk — it shapes
    attention and behavior by controlling what's in the context window.
    """

    def __init__(self, constitution: dict[str, Any]):
        self.constitution = constitution
        self._task_count = 0
        self._affirmation_config = constitution.get("affirmation", {})
        self._visualization_config = constitution.get("visualization", {})
        self._drives = constitution.get("internal_drives", {})
        self._core_imperatives = constitution.get("core_imperatives", {})
        self._negative_imperatives = constitution.get("negative_imperatives", {})
        self._refresh_count = self._affirmation_config.get("refresh_count", 5)
        self._constitution_refresh_interval = self._affirmation_config.get(
            "constitution_refresh_interval", 10
        )

    def tick(self) -> None:
        """Called once per agent task/step to advance the counter."""
        self._task_count += 1

    @property
    def task_count(self) -> int:
        return self._task_count

    def should_affirm(self) -> bool:
        """Whether it's time for an affirmation refresh."""
        if not self._affirmation_config.get("enabled", False):
            return False
        return self._task_count > 0 and self._task_count % self._refresh_count == 0

    def should_refresh_constitution(self) -> bool:
        """Whether it's time for a full constitution refresh."""
        if not self._affirmation_config.get("constitution_refresh", False):
            return False
        return self._task_count > 0 and self._task_count % self._constitution_refresh_interval == 0

    def build_affirmation_block(self) -> str:
        """Build the affirmation text to inject into the context window."""
        parts = []

        # Always include affirmation header
        parts.append("\n## 🔄 Affirmation Refresh (step %d)" % self._task_count)

        # Affirmation statements
        statements = self._affirmation_config.get("statements", [])
        if statements:
            parts.append("\n### Self-Talk")
            for stmt in statements:
                parts.append(f"- {stmt}")

        # Internal drives reminder
        if self._drives:
            parts.append("\n### Active Drives")
            for name, drive in self._drives.items():
                desc = drive.get("description", name) if isinstance(drive, dict) else str(drive)
                weight = drive.get("weight", "?") if isinstance(drive, dict) else "?"
                parts.append(f"- **{name}** (w={weight}): {desc}")

        return "\n".join(parts)

    def build_constitution_refresh(self) -> str:
        """Build a full constitution summary for context injection."""
        parts = []
        parts.append("\n## 📜 Constitution Refresh (step %d)" % self._task_count)

        # Core imperatives
        if self._core_imperatives:
            parts.append("\n### Core Imperatives (IMMUTABLE)")
            for name, imp in self._core_imperatives.items():
                desc = imp.get("description", name) if isinstance(imp, dict) else str(imp)
                parts.append(f"- **{name}**: {desc.strip()}")

        # Negative imperatives
        if self._negative_imperatives:
            parts.append("\n### Negative Imperatives (NEVER VIOLATE)")
            for name, imp in self._negative_imperatives.items():
                desc = imp.get("description", name) if isinstance(imp, dict) else str(imp)
                parts.append(f"- ⛔ **{name}**: {desc.strip()}")

        # Visualization prompts
        if self._visualization_config.get("enabled"):
            triggers = self._visualization_config.get("triggers", [])
            if triggers:
                parts.append("\n### Visualization")
                for t in triggers:
                    parts.append(f"- {t}")

        return "\n".join(parts)

    def get_context_injection(self) -> str:
        """Get the full context injection for this step (if any).

        Returns empty string if no injection is due.
        """
        parts = []

        if self.should_refresh_constitution():
            parts.append(self.build_constitution_refresh())

        if self.should_affirm():
            parts.append(self.build_affirmation_block())

        return "\n".join(parts)

    def build_initial_drives_prompt(self) -> str:
        """Build the initial drives section for the system prompt.

        This is included in every system prompt (not just refreshes)
        to ensure the agent is always aware of its constitution.
        """
        parts = []
        parts.append("\n## Constitution")
        parts.append("You are governed by a constitution with immutable core values.")

        # Summarize core imperatives briefly
        if self._core_imperatives:
            parts.append("\n### Core Values")
            for name, imp in self._core_imperatives.items():
                desc = imp.get("description", name) if isinstance(imp, dict) else str(imp)
                # Take first sentence only for the always-on summary
                first_sentence = desc.strip().split(".")[0] + "."
                parts.append(f"- {first_sentence}")

        # Summarize negative imperatives briefly
        if self._negative_imperatives:
            parts.append("\n### Boundaries (never cross)")
            for name, imp in self._negative_imperatives.items():
                desc = imp.get("description", name) if isinstance(imp, dict) else str(imp)
                first_sentence = desc.strip().split(".")[0] + "."
                parts.append(f"- ⛔ {first_sentence}")

        # Top drives
        if self._drives:
            parts.append("\n### Drives")
            sorted_drives = sorted(
                self._drives.items(),
                key=lambda x: x[1].get("weight", 0) if isinstance(x[1], dict) else 0,
                reverse=True,
            )
            for name, drive in sorted_drives[:5]:  # Top 5 only for brevity
                desc = drive.get("description", name) if isinstance(drive, dict) else str(drive)
                parts.append(f"- {desc}")

        return "\n".join(parts)
