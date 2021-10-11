#!/bin/bash -i
set -e
set -o pipefail

params="7b"

cd "$(dirname "$0")/.."
WORK="$(pwd)"

export PYTHONIOENCODING=utf-8
conda activate Cherokee-TTS

clear

cd "$WORK"/data
python prepare_spectrograms_nfc.py --directory "datasets/$params"

date

cd "$WORK"
python train.py --hyper_parameters "$params"

date
