"""Lightweight ablation data loader used by the comparison/coverage figure script."""

from __future__ import annotations

import json
from pathlib import Path


def load_answers(path: str | Path) -> list[dict]:
    """Load the ablation answer set from JSON.

    Supports the current list-of-dicts format and a dict wrapper with an
    `answers` or `question_results` field.
    """
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("answers", "question_results", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    raise ValueError(f"Unrecognised answer format in {p}")
