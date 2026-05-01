#!/bin/bash
# harvest.sh — save pipeline state to a zip and serve it for download
#
# Run on cloud:  bash harvest.sh
# Then on your LOCAL machine open:  http://<instance-ip>:<port>/
# and click the zip file to download it.
#
# Ports: vast.ai exposes whatever port you specify.  Default is 8000.
#   Override:  PORT=9000 bash harvest.sh

set -e
cd "$(dirname "$0")"

PORT="${PORT:-8000}"

echo "=== Stopping any running pipeline ==="
pkill -f "pipeline/runner.py" 2>/dev/null && echo "  Pipeline stopped." || echo "  (No pipeline running)"
sleep 2

echo ""
echo "=== Project Status ==="
python3 -c "
import json, pathlib
projects = sorted(pathlib.Path('.pipeline/projects').glob('*/state/current_idea.json'))
complete = []; active = []; stalled = []
for f in projects:
    try:
        d = json.loads(f.read_text())
    except Exception:
        continue
    slug = f.parent.parent.name
    st   = d.get('status', '?')
    ph   = d.get('phase', '?')
    tot  = d.get('total_phases', '?')
    line = f'  {slug[:38]:38s} {st:28s} phase={ph}/{tot}'
    if st in ('complete',): complete.append(line)
    elif st in ('budget_exceeded', 'stalled'): stalled.append(line)
    else: active.append(line)
print(f'Complete  ({len(complete)}):'); [print(l) for l in complete]
print(f'Active    ({len(active)}):');   [print(l) for l in active]
print(f'Stalled   ({len(stalled)}):');  [print(l) for l in stalled]
print(f'TOTAL: {len(projects)} projects')
"

echo ""
echo "=== Building zip ==="
python3 extract.py
# Grab the filename that was just created (newest zip in this dir)
ZIP=$(ls -t pipeline_extract_*.zip 2>/dev/null | head -1)

if [ -z "$ZIP" ]; then
    echo "ERROR: extract.py did not produce a zip file."
    exit 1
fi

SIZE=$(du -sh "$ZIP" | cut -f1)
echo "  Created: $ZIP  ($SIZE)"

echo ""
echo "============================================================"
echo "  HOW TO DOWNLOAD YOUR ZIP"
echo "============================================================"
echo ""
echo "  Option 1 — Upload to file.io (easiest, one-time link):"
echo "    curl -F \"file=@$ZIP\" https://file.io"
echo "    (Prints a download URL — open it in your local browser)"
echo ""
echo "  Option 2 — SCP (if you have SSH access to this instance):"
echo "    scp -P <ssh-port> root@<instance-ip>:\"/workspace/idea impl/$ZIP\" ."
echo ""
echo "  Option 3 — HTTP server (only works if port 8000 is mapped):"
echo "    PORT=8000 bash harvest.sh --serve"
echo ""
echo "============================================================"
echo ""

# If --serve flag passed, start the HTTP server
if [[ "${1:-}" == "--serve" ]]; then
    echo "  Serving on port ${PORT}..."
    echo "  Open: http://$(hostname -I | awk '{print $1}'):${PORT}/"
    echo "  Press Ctrl+C when download is complete."
    python3 -m http.server "$PORT"
fi
