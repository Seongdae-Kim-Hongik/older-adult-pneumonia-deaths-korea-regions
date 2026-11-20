#!/bin/bash
# run_all.sh - figures, manuscript, and Supplemental Material from the result tables.
set -e; cd "$(dirname "$0")"; O=../out
python3 figs.py
python3 build_ms.py
python3 esm.py
python3 post_esm.py $O/Supplement.docx
