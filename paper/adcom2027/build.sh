#!/usr/bin/env bash
# Rebuild numbers, tables, figures and the PDF. Requires: python venv with numpy/scipy/matplotlib/torch/stable-baselines3/fastapi/httpx,
# TeX Live with llncs (Springer class v2.24 as packaged), latexmk, bibtex.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
$PY figures/make_fig1_architecture.py
$PY figures/make_fig2_paths.py
$PY verification/make_numbers.py
$PY verification/make_tables.py
( cd manuscript && latexmk -pdf -interaction=nonstopmode main.tex )
cp manuscript/main.pdf ADCOM2027_submission_blind.pdf
$PY verification/verify_adcom.py
