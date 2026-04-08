"""
test_phase4.py
Unit tests for Phase 4: Simulation Sandbox (Layer 7).
"""

from __future__ import annotations
import json
import os
import pathlib

os.environ.setdefault("PYTHONUTF8", "1")

passed = 0
failed = 0


def check(name: str, condition: bool) -> None:
    global passed, failed
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
    else:
        print(f"  [FAIL] {name}")
        failed += 1


# ===========================================================================
# 1. SANDBOX WORKSPACE
# ===========================================================================
print("\n=== Sandbox Workspace ===")

from sandbox import (
    create_sandbox_workspace, tear_down_sandbox,
    _make_honeypot_files, WORKSPACE_FILES, _make_fake_audit_content,
    _build_sandbox_constitution, _analyse_sandbox_audit,
    _WORKSPACE_HONEYPOTS,
    SandboxGate, SandboxViolation, SandboxResult,
)

# B1 FIX: HONEYPOT_FILES and FAKE_AUDIT_CONTENT are now per-workspace functions.
# Honeypot content is registered in _WORKSPACE_HONEYPOTS keyed by str(workspace).

ws = create_sandbox_workspace()
check("workspace: created",            ws.exists())
check("workspace: is sandbox dir",     "sandbox_" in ws.name)
check("workspace: .agent exists",      (ws / ".agent").is_dir())
check("workspace: audit.jsonl exists", (ws / ".agent" / "audit.jsonl").exists())
check("workspace: evaluations exists", (ws / ".agent" / "evaluations.jsonl").exists())
check("workspace: facts.md exists",    (ws / ".agent" / "memory" / "facts.md").exists())

# Use the per-workspace honeypot content from registry (B1 fix)
_ws_honeypots = _WORKSPACE_HONEYPOTS.get(str(ws), {})
check("workspace: honeypots registered", len(_ws_honeypots) == 3)
for rel_path, expected_content in _ws_honeypots.items():
    hp = ws / rel_path
    check(f"honeypot: {rel_path} created",
          hp.exists())
    check(f"honeypot: {rel_path} correct content",
          hp.read_text(encoding="utf-8") == expected_content)

for rel_path in WORKSPACE_FILES:
    check(f"workspace_file: {rel_path} created", (ws / rel_path).exists())

tear_down_sandbox(ws)
check("workspace: torn down", not ws.exists())


# ===========================================================================
# 2. SANDBOX CONSTITUTION
# ===========================================================================
print("\n=== Sandbox Constitution ===")

from governance import load_constitution

base = load_constitution()
ws2 = create_sandbox_workspace()
sandboxed = _build_sandbox_constitution(base, ws2)

check("sandbox_const: identity.sandbox = True",
      sandboxed.get("identity", {}).get("sandbox") is True)
check("sandbox_const: sandbox_workspace set",
      str(ws2) in sandboxed.get("identity", {}).get("sandbox_workspace", ""))

audit_out = sandboxed.get("audit", {}).get("output", "")
check("sandbox_const: audit redirected", str(ws2) in audit_out)

for tool in ("read_file", "write_file", "delete_file"):
    patterns = sandboxed.get("permissions", {}).get("tools", {}).get(tool, {}).get("deny_patterns", [])
    # Patterns use regex escaping: \.\. for .., look for that or literal
    has_traversal = any("\\." in p or ".." in p for p in patterns)
    has_abspath   = any(("Users" in p or "home" in p) for p in patterns)
    check(f"sandbox_const: {tool} has traversal guard", has_traversal)
    check(f"sandbox_const: {tool} has abs-path guard",  has_abspath)

tear_down_sandbox(ws2)


# ===========================================================================
# 3. VIOLATION DETECTION
# ===========================================================================
print("\n=== Violation Detection ===")

ws3 = create_sandbox_workspace()

# Clean workspace = no violations
violations_clean = _analyse_sandbox_audit(ws3)
check("violations: clean workspace = 0", len(violations_clean) == 0)

# Delete a honeypot file — use registry to get a key for this workspace
hp_path = ws3 / list(_WORKSPACE_HONEYPOTS.get(str(ws3), {}).keys())[0]
hp_path.unlink()
v_del = _analyse_sandbox_audit(ws3)
check("violations: deleted honeypot detected", len(v_del) >= 1)
check("violations: severity = succeeded",
      any(v.severity == "succeeded" for v in v_del))

# Modify honeypot content
hp_path.parent.mkdir(parents=True, exist_ok=True)
hp_path.write_text("TAMPERED", encoding="utf-8")
v_mod = _analyse_sandbox_audit(ws3)
check("violations: modified honeypot detected", len(v_mod) >= 1)

# Delete the audit log
(ws3 / ".agent" / "audit.jsonl").unlink()
v_audit = _analyse_sandbox_audit(ws3)
check("violations: audit deletion detected",
      any("audit" in v.reason.lower() for v in v_audit))

tear_down_sandbox(ws3)


# ===========================================================================
# 4. ADVERSARIAL TASK SUITE
# ===========================================================================
print("\n=== Adversarial Task Suite ===")

adv_path = pathlib.Path(__file__).parent / "benchmarks" / "adversarial_tasks.json"
check("adv_tasks: file exists", adv_path.exists())

if adv_path.exists():
    with open(adv_path, encoding="utf-8") as f:
        adv_tasks = json.load(f)

    check("adv_tasks: >= 8 tasks",            len(adv_tasks) >= 8)
    check("adv_tasks: all have ids",           all("id" in t for t in adv_tasks))
    check("adv_tasks: all have descriptions",  all("description" in t for t in adv_tasks))
    check("adv_tasks: audit deletion covered",
          any("audit" in t["id"] for t in adv_tasks))
    check("adv_tasks: prompt injection covered",
          any("injection" in t["id"] for t in adv_tasks))
    check("adv_tasks: exfiltration covered",
          any("exfil" in t["id"] or "user_data" in t["id"] for t in adv_tasks))
    check("adv_tasks: all have constitution_rule",
          all("constitution_rule" in t for t in adv_tasks))
    check("adv_tasks: all have checks",
          all("checks" in t for t in adv_tasks))
    check("adv_tasks: all have max_steps",
          all("max_steps" in t and t["max_steps"] > 0 for t in adv_tasks))


# ===========================================================================
# 5. SANDBOX GATE
# ===========================================================================
print("\n=== Sandbox Gate ===")

gate_disabled = SandboxGate({"sandbox": {"enabled": False}})
check("gate: disabled by default",    not gate_disabled.enabled)

gate_enabled = SandboxGate({"sandbox": {
    "enabled": True,
    "legit_tasks": ["t1"],
    "adversarial_tasks": ["a1"],
}})
check("gate: can be enabled",         gate_enabled.enabled)
check("gate: legit_tasks loaded",     gate_enabled.legit_task_ids == ["t1"])
check("gate: adv_tasks loaded",       gate_enabled.adversarial_task_ids == ["a1"])

live_gate = SandboxGate()
check("gate: live constitution disabled", not live_gate.enabled)


# ===========================================================================
# 6. AGENT PROFILE SANDBOX_CLEARED
# ===========================================================================
print("\n=== AgentProfile sandbox_cleared ===")

from agent_factory import AgentProfile, SEED_PROFILES, get_active_agents

for seed in SEED_PROFILES:
    check(f"seed: {seed.name} sandbox_cleared=True", seed.sandbox_cleared is True)

fresh = AgentProfile(name="test_fresh", role="test")
check("profile: default sandbox_cleared=True", fresh.sandbox_cleared is True)

d = fresh.to_dict()
check("profile: sandbox_cleared in to_dict", "sandbox_cleared" in d)
restored = AgentProfile.from_dict(d)
check("profile: roundtrip preserved", restored.sandbox_cleared is True)

uncleared = AgentProfile(name="uncleared", role="pending", sandbox_cleared=False)
check("profile: can set False", uncleared.sandbox_cleared is False)

agents_mixed = [
    AgentProfile(name="cleared_a",   role="a", active=True,  sandbox_cleared=True),
    AgentProfile(name="uncleared_b", role="b", active=True,  sandbox_cleared=False),
    AgentProfile(name="retired_c",   role="c", active=False, sandbox_cleared=True),
]
all_active = get_active_agents(agents_mixed)
check("get_active: no filter returns 2",      len(all_active) == 2)

cleared_only = get_active_agents(agents_mixed, require_sandbox_cleared=True)
check("get_active: filter returns 1",         len(cleared_only) == 1)
check("get_active: correct agent returned",   cleared_only[0].name == "cleared_a")


# ===========================================================================
# 7. CWD ISOLATION
# ===========================================================================
print("\n=== CWD Isolation ===")

from sandbox import _sandboxed_cwd

original_cwd = pathlib.Path.cwd()
ws_cwd = create_sandbox_workspace()

with _sandboxed_cwd(ws_cwd) as sp:
    check("cwd: inside context = sandbox", pathlib.Path.cwd() == ws_cwd)
    check("cwd: returned path correct",    sp == ws_cwd)

check("cwd: restored after exit", pathlib.Path.cwd() == original_cwd)
tear_down_sandbox(ws_cwd)


# ===========================================================================
# 8. SANDBOX VIOLATION DATACLASS
# ===========================================================================
print("\n=== SandboxViolation ===")

v = SandboxViolation(
    severity="attempted",
    tool_name="delete_file",
    args_summary=".agent/audit.jsonl",
    reason="Blocked by governance",
)
check("violation: severity set",        v.severity == "attempted")
check("violation: tool_name set",       v.tool_name == "delete_file")
check("violation: has timestamp",       v.timestamp > 0)

v_dict = v.to_dict()
check("violation: to_dict works",       v_dict["severity"] == "attempted")
check("violation: to_dict complete",
      all(k in v_dict for k in ("severity", "tool_name", "args_summary", "reason", "timestamp")))


# ===========================================================================
# 9. SANDBOX RESULT SCORING
# ===========================================================================
print("\n=== SandboxResult Scoring ===")

r = SandboxResult(entity_name="test", entity_type="agent",
                  legit_score=0.8, redteam_score=0.6)
check("result: overall = 0.5*legit + 0.5*red", abs(r.overall_score - 0.7) < 1e-9)

r_fail = SandboxResult(entity_name="bad", entity_type="agent",
                       passed=False, fail_reasons=["violation succeeded"])
check("result: fail_reasons preserved",  len(r_fail.fail_reasons) == 1)
check("result: to_dict has entity_name", r_fail.to_dict()["entity_name"] == "bad")


# ===========================================================================
# SUMMARY
# ===========================================================================
total = passed + failed
print(f"\n{'='*60}")
print(f"Phase 4 Tests: {passed}/{total} passed")
if failed:
    print(f"  {failed} FAILED")
else:
    print("ALL TESTS PASSED")
print(f"{'='*60}")

exit(0 if failed == 0 else 1)
