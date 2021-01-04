#!/bin/bash -ix
set -e
set -o pipefail
clear

conda activate Cherokee-TTS

params="cherokee2c"
cp="cherokee2c-decomposed_loss-40-0.275"

cd "$(dirname "$0")"
WORK="$(pwd)"

#cp -v data/"$params"/checkpoint/"$cp" checkpoints/

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --checkpoint "$cp" --accumulation_size 1

date