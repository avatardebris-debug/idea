#!/bin/bash
# harvest.sh — commit all pipeline state to git so nothing is ever lost
# Run on cloud: bash harvest.sh
# This is the ONLY safe way to preserve work. The zip download only captures
# what's on disk — this ensures everything is in git too.

set -e
cd "$(dirname "$0")"

echo "=== Stopping any running pipeline ==="
pkill -f "pipeline/runner.py" 2>/dev/null || true
sleep 1

echo ""
echo "=== Running fix_missing_plans.py (reconstruct any missing master_plan.md) ==="
python fix_missing_plans.py 2>/dev/null | grep -E "(plan created|state fixed|Done:)" || true

echo ""
echo "=== Committing ALL .pipeline/projects/ state to git ==="
git add .pipeline/projects/ master_ideas.md 2>/dev/null || true

# Only commit if there's something to commit
if git diff --cached --quiet; then
    echo "  Nothing new to commit — already up to date"
else
    TIMESTAMP=$(date +%Y%m%d_%H%M)
    PROJ_COUNT=$(git diff --cached --name-only | grep "current_idea.json" | wc -l)
    git commit -m "harvest: pipeline state snapshot $TIMESTAMP ($PROJ_COUNT projects)"
    echo "  ✓ Committed"
fi

echo ""
echo "=== Pushing to remote ==="
git push
echo "  ✓ Pushed"

echo ""
echo "=== Project Summary ==="
python -c "
import json, pathlib
projects = sorted(pathlib.Path('.pipeline/projects').glob('*/state/current_idea.json'))
complete = []; active = []; stalled = []
for f in projects:
    d = json.loads(f.read_text())
    slug = f.parent.parent.name
    st   = d.get('status', '?')
    ph   = d.get('phase', '?')
    tot  = d.get('total_phases', '?')
    has_plan = (f.parent / 'master_plan.md').exists()
    plan_flag = '' if has_plan else ' ⚠ NO PLAN'
    line = f'  {slug[:40]:40s} {st:28s} phase={ph}/{tot}{plan_flag}'
    if st in ('complete',): complete.append(line)
    elif st in ('budget_exceeded', 'stalled'): stalled.append(line)
    else: active.append(line)
print(f'Complete ({len(complete)}):')
for l in complete: print(l)
print(f'Active ({len(active)}):')
for l in active: print(l)
print(f'Stalled ({len(stalled)}):')
for l in stalled: print(l)
"
