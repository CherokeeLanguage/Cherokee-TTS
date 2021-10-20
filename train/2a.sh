#!/bin/bash -i
set -e
set -o pipefail

params="2a"

cd "$(dirname "$0")/.."
WORK="$(pwd)"

export PYTHONIOENCODING=utf-8
conda activate Cherokee-TTS

clear

cd "$WORK"/data
python prepare_spectrograms_uv.py --dataset "$params"

date

cd "$WORK"
python train.py --hyper_parameters "$params"

date
