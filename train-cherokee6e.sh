#!/bin/bash -x
set -e
set -o pipefail
clear

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_cherokee_spectrograms.py --cherokee_directory cherokee6e

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python train-ga.py --hyper_parameters generated_switching_cherokee6e --accumulation_size 4

date