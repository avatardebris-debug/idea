#!/bin/bash
# =============================================================================
# cloud_setup.sh — One-shot cloud compute setup for Cognitive Architecture
# =============================================================================
# Run this on a fresh cloud instance (Vast.ai, RunPod, Lambda, etc.)
#
# Requirements:
#   - Ubuntu/Debian with NVIDIA GPU (24GB+ VRAM recommended for Qwen3 30B-A3B)
#   - SSH access
#
# Usage:
#   chmod +x cloud_setup.sh
#   ./cloud_setup.sh
# =============================================================================

set -euo pipefail

echo "==========================================="
echo "  Cognitive Architecture — Cloud Setup"
echo "==========================================="

# --- 1. System dependencies ---
echo "[1/6] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git curl jq

# --- 2. Install Ollama ---
echo "[2/6] Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "  Ollama already installed: $(ollama --version)"
fi

# --- 3. Start Ollama in the background ---
echo "[3/6] Starting Ollama server..."
# Kill any existing instance
pkill ollama 2>/dev/null || true
sleep 1

# Start fresh — bind to all interfaces so SSH tunnels work
OLLAMA_HOST=0.0.0.0:11434 nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 3

# Verify it's running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "  ✓ Ollama running on :11434"
else
    echo "  ✗ Ollama failed to start. Check /tmp/ollama.log"
    exit 1
fi

# --- 4. Pull the model ---
echo "[4/6] Pulling Qwen3 model (this takes a few minutes on first run)..."

# Model selection based on available VRAM:
#   80GB+ VRAM: qwen3.5:72b-q4_K_M     (best quality, dense)
#   48GB  VRAM: qwen3.5:35b             (MoE, fast, great tool-calling)
#   24GB  VRAM: qwen3.5:27b-q4_K_M      (dense 27B quantised, fits 3090/4090)
#   16GB  VRAM: qwen3.5:35b-q4_K_M      (MoE quantised, ~3B active params)

# Detect VRAM
if command -v nvidia-smi &> /dev/null; then
    VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1 | tr -d ' ')
    echo "  Detected ${VRAM_MB}MB VRAM"

    if [ "$VRAM_MB" -ge 78000 ]; then
        MODEL="qwen3.5:72b-q4_K_M"
    elif [ "$VRAM_MB" -ge 45000 ]; then
        MODEL="qwen3.5:35b"
    elif [ "$VRAM_MB" -ge 22000 ]; then
        MODEL="qwen3.5:27b-q4_K_M"
    else
        MODEL="qwen3.5:35b-q4_K_M"
    fi
else
    echo "  No GPU detected — using MoE model (runs on CPU, slowly)"
    MODEL="qwen3.5:35b-q4_K_M"
fi

echo "  Selected model: ${MODEL}"
ollama pull "${MODEL}"
echo "  ✓ Model pulled"

# --- 5. Set up the Python environment ---
echo "[5/6] Setting up Python environment..."
AGENT_DIR="${AGENT_DIR:-$(pwd)}"

if [ ! -d "${AGENT_DIR}/.venv" ]; then
    python3 -m venv "${AGENT_DIR}/.venv"
fi
source "${AGENT_DIR}/.venv/bin/activate"

pip install -q --upgrade pip
pip install -q ollama

echo "  Downloading HumanEval dataset..."
python3 -c "
import urllib.request, pathlib
dest = pathlib.Path('benchmarks/datasets/HumanEval.jsonl.gz')
dest.parent.mkdir(parents=True, exist_ok=True)
if not dest.exists():
    urllib.request.urlretrieve(
        'https://github.com/openai/human-eval/raw/master/data/HumanEval.jsonl.gz',
        str(dest)
    )
    print('  Downloaded HumanEval.jsonl.gz')
else:
    print('  HumanEval dataset already present')
"

echo "  ✓ Python environment ready"

# --- 6. Write the model config ---
echo "[6/6] Writing runtime config..."
cat > "${AGENT_DIR}/.agent/cloud_config.json" << EOF
{
    "provider": "ollama",
    "model": "${MODEL}",
    "base_url": "http://localhost:11434",
    "temperature": 0.2,
    "setup_date": "$(date -Iseconds)",
    "gpu": "$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'none')",
    "vram_mb": ${VRAM_MB:-0}
}
EOF

echo ""
echo "==========================================="
echo "  ✓ Setup complete!"
echo "==========================================="
echo ""
echo "  Model:    ${MODEL}"
echo "  Provider: ollama"
echo "  Base URL: http://localhost:11434"
echo ""
echo "  To start an experiment session:"
echo ""
echo "    source .venv/bin/activate"
echo "    export PYTHONUTF8=1"
echo "    python experimenter.py \\"
echo "        --provider ollama \\"
echo "        --model ${MODEL} \\"
echo "        --time-limit 480 \\"
echo "        --autoapprove"
echo ""
echo "  To resume from a previous run:"
echo ""
echo "    # 1. Upload your state bundle:"
echo "    python state_bundle.py import state_YYYYMMDD_HHMMSS.tar.gz"
echo ""
echo "    # 2. Run (it auto-resumes from checkpoint):"
echo "    python experimenter.py --provider ollama --model ${MODEL} --time-limit 480"
echo ""
