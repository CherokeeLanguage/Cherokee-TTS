#!/bin/bash -x
set -e
set -o pipefail
clear

params="cherokee6i"
cp="cherokee6i_loss-192-0.216"

cd "$(dirname "$0")"
WORK="$(pwd)"

cp data/"$params"/checkpoint/"$cp" checkpoints/

cd data
python prepare_spectrograms.py --sample_rate 22050 --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --logging_start 0 --reset_epoch True --accumulation_size 5 --checkpoint "$cp"

date