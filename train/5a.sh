#!/bin/bash -i
set -e
set -o pipefail
clear

conda activate Cherokee-TTS

params="5a"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_spectrograms.py --directory "datasets/$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --hyper_parameters "$params" --accumulation_size 3

date