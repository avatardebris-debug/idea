import pathlib

f = pathlib.Path("pipeline/runner.py")
lines = f.read_text(encoding="utf-8").splitlines()

# Find the broken block: line 533 has extra indent
# Replace lines 533-549 with correct indentation
new_block = [
    "            if tasks_file.exists():",
    "                try:",
    "                    from pipeline.agent_process import AgentProcess",
    "                    # Normalize format first (## Task N: -> - [ ] Task N:)",
    "                    if AgentProcess.normalize_tasks_file(tasks_file):",
    "                        print(f\"  Normalized task format for '{title}' phase {phase_num}\")",
    "                    raw = tasks_file.read_text(encoding=\"utf-8\")",
    "                    scoped = AgentProcess._extract_phase_tasks(raw, phase_num)",
    "                    task_lines = scoped.split(\"\\n\")",
    "                    task_indices = [i for i, l in enumerate(task_lines) if l.strip().startswith(\"- [ ]\") or l.strip().startswith(\"- [x]\")]",
    "                    if len(task_indices) > MAX_TASKS:",
    "                        cut_at = task_indices[MAX_TASKS]",
    "                        trimmed = \"\\n\".join(task_lines[:cut_at])",
    "                        trimmed += f\"\\n\\n<!-- {len(task_indices) - MAX_TASKS} tasks removed by retroactive guardrail -->\\n\"",
    "                        tasks_file.write_text(trimmed, encoding=\"utf-8\")",
    "                        print(f\"  Trimmed '{title}' phase {phase_num}: {len(task_indices)} to {MAX_TASKS} tasks\")",
    "                except Exception:",
    "                    pass",
]

# Lines are 0-indexed; line numbers in output are 1-indexed
# The broken section starts at line index 532 (line 533) and goes to 548 (line 549)
start_idx = 532  # 0-indexed
end_idx = 549    # exclusive

# Verify
print("Before:")
for i, l in enumerate(lines[start_idx:end_idx], start_idx+1):
    print(f"  {i}: {repr(l[:60])}")

lines[start_idx:end_idx] = new_block
f.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\nDone! Wrote", len(lines), "lines")
