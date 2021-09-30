#!/bin/bash -i
set -e
set -o pipefail

params="5d"

cd "$(dirname "$0")/.."
WORK="$(pwd)"

export PYTHONIOENCODING=utf-8
conda activate Cherokee-TTS

clear

cd "$WORK"/data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
python trainGa.py --hyper_parameters "$params" --accumulation_size 3

date
