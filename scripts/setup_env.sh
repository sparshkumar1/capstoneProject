#!/usr/bin/env bash
set -e

echo "============================================================"
echo "  PrepAIred - Reproducible Environment Setup (Linux/macOS)  "
echo "============================================================"

# 1. Create Virtual Environment if not exists
if [ ! -d ".venv" ]; then
    echo "[1/4] Creating Python virtual environment in .venv..."
    python3 -m venv .venv
else
    echo "[1/4] Virtual environment .venv already exists."
fi

# 2. Activate Virtual Environment
source .venv/bin/activate

# 3. Upgrade pip and wheel
echo "[2/4] Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# 4. Install Base & Subsystem Dependencies
echo "[3/4] Installing backend, evaluator, RL, and dev dependencies..."
pip install -r requirements/base.txt
pip install -r requirements/backend.txt
pip install -r requirements/evaluator.txt
pip install -r requirements/rl.txt
pip install -r requirements/dev.txt

# 5. Install PyTorch CPU & Audio Stack (or GPU if --cuda passed)
if [ "$1" == "--cuda" ]; then
    echo "[4/4] Installing CUDA-enabled PyTorch & WhisperX dependencies..."
    pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu121
    pip install -r requirements/audio.txt
else
    echo "[4/4] Installing CPU PyTorch & WhisperX audio dependencies (Default)...
    pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cpu
    pip install -r requirements/audio.txt
fi

echo ""
echo "============================================================"
echo "  Setup Complete!"
echo "  Run 'python scripts/verify_whisperx_runtime.py' to test audio STT."
echo "  Run 'pytest' to execute test suite."
echo "============================================================"
