#!/bin/bash -i
set -e
set -o pipefail

params="2b"

cd "$(dirname "$0")/.."
WORK="$(pwd)"

export PYTHONIOENCODING=utf-8
conda activate Cherokee-TTS

clear

cd "$WORK"/data
python prepare_spectrograms.py --directory "datasets/$params"

date

cd "$WORK"
python train.py --hyper_parameters "$params"

date
