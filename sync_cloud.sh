#!/usr/bin/env bash
# sync_cloud.sh — Safe cloud sync: pull latest code + restore all tracked pipeline files
# Usage: bash sync_cloud.sh
set -e

echo "=== Stopping any running pipeline (kill runner) ==="
pkill -f "pipeline/runner.py" 2>/dev/null || true
sleep 1

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
# This restores any locally-deleted tracked files from HEAD
git checkout HEAD -- .pipeline/ 2>/dev/null || true

echo "=== Current project states ==="
python -c "
import json, pathlib
for f in sorted(pathlib.Path('.pipeline/projects').glob('*/state/current_idea.json')):
    d = json.loads(f.read_text())
    st = d.get('status','?')
    ph = d.get('phase','?')
    print(f'  {f.parent.parent.name[:35]:35s} {st}')
"

echo ""
echo "=== Ready. Run: ==="
echo "  python pipeline/runner.py --from-list --provider ollama --model qwen3.5:35b --time-limit 600"
