#!/bin/bash -x
set -e
set -o pipefail
clear

params="cherokee6g"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_cherokee_spectrograms.py --cherokee_directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python train-ga.py --hyper_parameters "$params" --accumulation_size 4

date