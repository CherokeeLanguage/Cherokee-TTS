#!/bin/bash -x
set -e
set -o pipefail
clear

cd "$(dirname "$0")"
WORK="$(pwd)"

cp="CHEROKEE6C-WARMSTART"

cp "./data/cherokee6c/checkpoint/GENERATED-SWITCHING-CHEROKEE6B_loss-55-0.235" "checkpoints/$cp"

cd data
python prepare_cherokee_spectrograms.py --cherokee_directory cherokee6c

cd "$WORK"
printf "Using checkpoint: $cp\n"

date

export PYTHONIOENCODING=utf-8
python train-ga.py --reset_epoch True --checkpoint "$cp" --hyper_parameters generated_switching_cherokee6c --accumulation_size 5

date