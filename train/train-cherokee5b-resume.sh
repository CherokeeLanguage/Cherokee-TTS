#!/bin/bash -i
set -e
set -o pipefail
clear

conda activate Cherokee-TTS

params="cherokee5b"
cp="cherokee5b_loss-205-0.115"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --checkpoint "$cp" --accumulation_size 1

date