"""
build_colab_notebook.py — Generates experiments/experiment_3_feedback/qwen7b_colab_runner.ipynb
"""

import json
from pathlib import Path

# Read runner_qwen_colab.py to embed inside the notebook
runner_py_path = Path("experiments/experiment_3_feedback/runner_qwen_colab.py")
with open(runner_py_path, "r", encoding="utf-8") as f:
    runner_code = f.read()

notebook_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# EXP-3: Qwen2.5-7B-Instruct Formative Feedback Evaluation on Google Colab GPU\n",
            "\n",
            "**Experiment ID:** EXP-3 — Formative Feedback Grounding & Actionability Comparison  \n",
            "**Preregistered Condition:** `qwen_7b_grounded_feedback`  \n",
            "**Model:** `Qwen/Qwen2.5-7B-Instruct`  \n",
            "**Exact Revision:** `a09a35458c702b33eeacc393d103063234e8bc28`  \n",
            "**Target Scope:** Exactly 20/20 Preregistered Benchmark Turns  \n",
            "\n",
            "---\n",
            "\n",
            "### Prerequisites:\n",
            "In the Colab menu bar, select:\n",
            "**Runtime** &rarr; **Change runtime type** &rarr; **Hardware accelerator: T4 GPU / V100 / A100**."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 1: Install Required Dependencies\n",
            "!pip install -q transformers torch huggingface_hub safetensors accelerate scipy"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 2: Environment and CUDA Hardware Verification\n",
            "import sys\n",
            "import torch\n",
            "import transformers\n",
            "\n",
            "print('=' * 60)\n",
            "print('ENVIRONMENT & CUDA VERIFICATION')\n",
            "print('=' * 60)\n",
            "print(f'Python Version:       {sys.version.split()[0]}')\n",
            "print(f'PyTorch Version:      {torch.__version__}')\n",
            "print(f'Transformers Version: {transformers.__version__}')\n",
            "print(f'CUDA Available:       {torch.cuda.is_available()}')\n",
            "\n",
            "if not torch.cuda.is_available():\n",
            "    raise RuntimeError('FATAL: No CUDA GPU detected! Please select Runtime -> Change runtime type -> T4 GPU.')\n",
            "\n",
            "gpu_name = torch.cuda.get_device_name(0)\n",
            "vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)\n",
            "print(f'Detected GPU:         {gpu_name}')\n",
            "print(f'GPU VRAM:             {vram_gb:.2f} GB')\n",
            "print(f'CUDA Version:         {torch.version.cuda}')\n",
            "print('=' * 60)\n",
            "print('CUDA GPU VERIFICATION PASSED.')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 3: Write Standalone Runner Script and Benchmark Dataset\n",
            "with open('runner_qwen_colab.py', 'w', encoding='utf-8') as f:\n",
            "    f.write('''" + runner_code.replace("\\", "\\\\").replace("'''", "\\'\\'\\'") + "''')\n",
            "\n",
            "print('Runner script written: runner_qwen_colab.py')"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 4: Execute Complete EXP-3 Qwen-7B Condition on CUDA GPU\n",
            "!python runner_qwen_colab.py results"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Step 5: Display Summary Results & Download Artifacts\n",
            "import os\n",
            "import json\n",
            "import pandas as pd\n",
            "\n",
            "raw_path = 'results/experiment_3_qwen_raw.json'\n",
            "proc_path = 'results/experiment_3_qwen_processed.csv'\n",
            "\n",
            "if os.path.exists(raw_path):\n",
            "    with open(raw_path, 'r', encoding='utf-8') as f:\n",
            "        data = json.load(f)\n",
            "    print('Status:', data['status'])\n",
            "    print('Completed Samples:', data['total_samples_completed'])\n",
            "    print('Aggregated Metrics:', json.dumps(data['aggregated_metrics'], indent=2))\n",
            "\n",
            "if os.path.exists(proc_path):\n",
            "    df = pd.read_csv(proc_path)\n",
            "    display(df[['item_id', 'score', 'grounding_ratio', 'gap_coverage', 'actionability_count', 'runtime_seconds']])\n",
            "\n",
            "# Colab file download helper\n",
            "try:\n",
            "    from google.colab import files\n",
            "    files.download('results/experiment_3_qwen_raw.json')\n",
            "    files.download('results/experiment_3_qwen_processed.csv')\n",
            "    print('Files queued for download.')\n",
            "except Exception as e:\n",
            "    print('Download helper note:', e)"
        ]
    }
]

notebook_json = {
    "cells": notebook_cells,
    "metadata": {
        "accelerator": "GPU",
        "colab": {
            "gpuType": "T4",
            "provenance": []
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 0
}

out_nb_path = Path("experiments/experiment_3_feedback/qwen7b_colab_runner.ipynb")
with open(out_nb_path, "w", encoding="utf-8") as f:
    json.dump(notebook_json, f, indent=2)

print(f"Generated Colab notebook: {out_nb_path}")
