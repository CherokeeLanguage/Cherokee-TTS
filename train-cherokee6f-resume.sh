#!/bin/bash -x
set -e
set -o pipefail
clear

params="cherokee6f"
cp="GENERATED-SWITCHING-CHEROKEE6F_loss-44-0.226"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python train-ga.py --accumulation_size 4 --checkpoint "$cp"

date