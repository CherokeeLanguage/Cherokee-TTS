#!/bin/bash -x
set -e
set -o pipefail
clear

cd "$(dirname "$0")"
WORK="$(pwd)"
cd data
python prepare_cherokee4_spectrograms.py

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python train-ga.py --hyper_parameters generated_switching_cherokee4 --accumulation_size 2

date