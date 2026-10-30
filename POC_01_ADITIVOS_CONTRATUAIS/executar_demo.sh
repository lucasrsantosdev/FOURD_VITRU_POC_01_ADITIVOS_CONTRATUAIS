#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python -m poc_aditivos --saida ./saida_demo
python -m unittest discover -s tests -v
