"""
PrepAIred — Deterministic Qwen 1.5B GGUF Model Downloader
=========================================================
Downloads the exact quantized GGUF model weights (Q4_K_M, ~1.06 GB)
required for local CPU inference in the live interactive demo.

No Hugging Face token or login required (Public Model).

Destination:
    models/gguf/qwen2.5-1.5b-instruct-q4_k_m.gguf
"""

import os
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_DIR = REPO_ROOT / "models" / "gguf"
TARGET_FILE = TARGET_DIR / "qwen2.5-1.5b-instruct-q4_k_m.gguf"

MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
EXPECTED_MIN_BYTES = 1_000_000_000  # ~1.04 GB minimum


def download_progress(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size) if total_size > 0 else 0
    downloaded_mb = (count * block_size) / (1024 * 1024)
    total_mb = total_size / (1024 * 1024) if total_size > 0 else 0
    sys.stdout.write(f"\rDownloading: {downloaded_mb:.1f} MB / {total_mb:.1f} MB [{percent}%]")
    sys.stdout.flush()


def main():
    print("=" * 70)
    print("PrepAIred — Qwen 1.5B GGUF Model Downloader")
    print("=" * 70)
    print(f"Target Directory: {TARGET_DIR}")
    print(f"Target File:      {TARGET_FILE.name}")
    print(f"Source URL:       {MODEL_URL}")
    print("=" * 70)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    if TARGET_FILE.exists():
        size = TARGET_FILE.stat().st_size
        if size >= EXPECTED_MIN_BYTES:
            print(f"[OK] Model already exists at {TARGET_FILE} ({size / (1024*1024):.1f} MB).")
            print("Download not needed. Ready for local CPU demo.")
            return 0
        else:
            print(f"[WARN] Incomplete file detected ({size} bytes). Re-downloading...")
            TARGET_FILE.unlink()

    # Try huggingface_hub if available, otherwise urllib
    try:
        from huggingface_hub import hf_hub_download
        print("[INFO] Downloading via huggingface_hub...")
        hf_hub_download(
            repo_id="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
            filename="qwen2.5-1.5b-instruct-q4_k_m.gguf",
            local_dir=str(TARGET_DIR),
            local_dir_use_symlinks=False,
        )
    except Exception as exc:
        print(f"[INFO] Falling back to direct HTTP stream download ({exc})...")
        t0 = time.time()
        urllib.request.urlretrieve(MODEL_URL, str(TARGET_FILE), reporthook=download_progress)
        print()
        elapsed = time.time() - t0
        print(f"[INFO] Download completed in {elapsed:.1f}s.")

    if TARGET_FILE.exists() and TARGET_FILE.stat().st_size >= EXPECTED_MIN_BYTES:
        size_mb = TARGET_FILE.stat().st_size / (1024 * 1024)
        print(f"[SUCCESS] Model successfully saved to {TARGET_FILE} ({size_mb:.1f} MB).")
        print("You can now start the Qwen service with: python services/qwen/app.py")
        return 0
    else:
        print("[ERROR] Download verification failed. File missing or too small.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
