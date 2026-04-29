#!/usr/bin/env bash
# sync_cloud.sh — Safe cloud sync: rescue stray files, pull latest code + restore tracked files
# Usage: bash sync_cloud.sh
set -e

PIPELINE_DIR="/workspace/idea impl/.pipeline"
STRAY_ROOT="/workspace/workspace"

echo "=== Stopping any running pipeline ==="
pkill -f "pipeline/runner.py" 2>/dev/null || true
sleep 1

echo "=== Rescuing stray files from /workspace/workspace/ ==="
# Root cause: LLM writes 'workspace/' relative to cwd /workspace/ instead of
# the absolute .pipeline path. This moves them to the correct location.
if [ -d "$STRAY_ROOT" ]; then
    for stray_proj in "$STRAY_ROOT"/*/; do
        [ -d "$stray_proj" ] || continue
        slug=$(basename "$stray_proj")
        target_ws="$PIPELINE_DIR/projects/$slug/workspace"

        if [ ! -d "$PIPELINE_DIR/projects/$slug" ]; then
            echo "  ⚠  No matching project for stray '$slug' — skipping"
            continue
        fi

        echo "  Rescuing: /workspace/workspace/$slug → .pipeline/projects/$slug/workspace/"
        mkdir -p "$target_ws"

        # Move source files (skip __pycache__, .pytest_cache, phases/)
        find "$stray_proj" -maxdepth 5 -type f \
            ! -path "*/__pycache__/*" \
            ! -path "*/.pytest_cache/*" \
            ! -path "*/phases/*" \
            | while IFS= read -r src; do
                rel="${src#"$stray_proj"}"
                dst="$target_ws/$rel"
                if [ ! -f "$dst" ]; then
                    mkdir -p "$(dirname "$dst")"
                    cp "$src" "$dst"
                    echo "    + $rel"
                elif [ "$src" -nt "$dst" ]; then
                    cp "$src" "$dst"
                    echo "    ~ $rel (updated)"
                fi
            done

        # Move phase reports (validation_report.md, review.md) to correct phases/ dir
        if [ -d "${stray_proj}phases" ]; then
            find "${stray_proj}phases" -type f | while IFS= read -r src; do
                rel="${src#"${stray_proj}phases/"}"
                dst="$PIPELINE_DIR/projects/$slug/phases/$rel"
                if [ ! -f "$dst" ]; then
                    mkdir -p "$(dirname "$dst")"
                    cp "$src" "$dst"
                    echo "    + phases/$rel"
                fi
            done
        fi
    done
    echo "  Stray rescue complete."
else
    echo "  No /workspace/workspace/ found — nothing to rescue"
fi

echo ""
echo "=== Clearing queue messages ==="
python -c "
from pipeline.message_bus import MessageBus
from pipeline.runner import AGENT_ROLES
bus = MessageBus()
cleared = sum(bus.clear_queue(r) for r in AGENT_ROLES)
print(f'  Cleared {cleared} messages')
"

echo "=== Pulling latest code ==="
git fetch origin
git merge origin/main --no-edit

echo "=== Restoring ALL tracked pipeline files (safe, no delete) ==="
git checkout HEAD -- .pipeline/ 2>/dev/null || true

echo "=== Current project states ==="
python -c "
import json, pathlib
projects = sorted(pathlib.Path('.pipeline/projects').glob('*/state/current_idea.json'))
if not projects:
    print('  (no projects)')
for f in projects:
    d = json.loads(f.read_text())
    slug = f.parent.parent.name
    st   = d.get('status','?')
    ph   = d.get('phase','?')
    tot  = d.get('total_phases','?')
    ws   = f.parent.parent / 'workspace'
    py   = [p for p in ws.rglob('*.py') if '__pycache__' not in str(p)] if ws.exists() else []
    print(f'  {slug[:35]:35s} {st:30s} phase={ph}/{tot}  py={len(py)}')
"

echo ""
echo "=== Ready. Run: ==="
echo "  python pipeline/runner.py --from-list --provider ollama --model qwen3.5:35b --time-limit 600"
