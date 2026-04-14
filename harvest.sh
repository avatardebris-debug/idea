#!/bin/bash
# harvest.sh — collect pipeline output and push back to git
# Run on cloud after pipeline finishes: bash harvest.sh

set -e
cd "$(dirname "$0")"

TIMESTAMP=$(date +%Y%m%d_%H%M)
OUT_DIR="output/$TIMESTAMP"

mkdir -p "$OUT_DIR"

# Copy generated code
if [ -d ".pipeline/workspace" ]; then
    cp -r .pipeline/workspace "$OUT_DIR/"
    echo "✓ Copied workspace"
fi

# Copy manager decisions log
if [ -f ".pipeline/state/manager_decisions.md" ]; then
    cp .pipeline/state/manager_decisions.md "$OUT_DIR/"
    echo "✓ Copied manager_decisions.md"
fi

# Copy ideator brainstorms
if [ -d ".pipeline/ideator_output" ]; then
    cp -r .pipeline/ideator_output "$OUT_DIR/"
    echo "✓ Copied ideator_output"
fi

# Copy updated idea list
cp master_ideas.md "$OUT_DIR/"
echo "✓ Copied master_ideas.md"

# Push to git
git add "output/"
git commit -m "Pipeline output — $TIMESTAMP"
git push

echo ""
echo "Done! Pull locally with: git pull"
echo "Output is in: output/$TIMESTAMP/"
