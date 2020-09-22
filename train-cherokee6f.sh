#!/bin/bash -x
set -e
set -o pipefail
clear

params="cherokee6f"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python train-ga.py --hyper_parameters "$params" --accumulation_size 4

date