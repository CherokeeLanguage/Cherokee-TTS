#!/bin/bash -i
set -e
set -o pipefail

params="2e"

cd "$(dirname "$0")/.."
WORK="$(pwd)"

export PYTHONIOENCODING=utf-8
conda activate Cherokee-TTS

clear
python prepare_spectrograms.py --directory "datasets/$params"

date

cd "$WORK"
python train.py --hyper_parameters "$params"

date
