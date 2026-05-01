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
echo "  Download your zip:"
echo ""
echo "  Open this URL in your browser:"
echo "    http://$(hostname -I | awk '{print $1}'):${PORT}/"
echo ""
echo "  Or if using vast.ai port mapping, use your instance's"
echo "  mapped external port for port ${PORT}."
echo ""
echo "  Serving files from: $(pwd)"
echo "  Press Ctrl+C when download is complete."
echo "============================================================"
echo ""

# Serve the current directory so user can click the zip to download
python3 -m http.server "$PORT"
