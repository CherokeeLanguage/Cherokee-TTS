#!/bin/bash -i
set -e
set -o pipefail

params="2e"

cd "$(dirname "$0")/.."
WORK="$(pwd)"

export PYTHONIOENCODING=utf-8
conda activate Cherokee-TTS

clear

cd "$WORK"/data
python prepare_spectrograms.py --directory "datasets/$params"

date

cd "$WORK"
python trainGa.py --hyper_parameters "$params" --accumulation_size 4

date
