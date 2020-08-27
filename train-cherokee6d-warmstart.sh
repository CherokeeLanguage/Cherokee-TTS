#!/bin/bash -x
set -e
set -o pipefail
clear

cd "$(dirname "$0")"
WORK="$(pwd)"

cp="CHEROKEE6D-WARMSTART"

cp "./data/cherokee6d/checkpoint/GENERATED-SWITCHING-CHEROKEE6C_loss-135-0.195" "checkpoints/$cp"

cd data
python prepare_cherokee_spectrograms.py --cherokee_directory cherokee6d

cd "$WORK"
printf "Using checkpoint: $cp\n"

date

export PYTHONIOENCODING=utf-8
python train-ga.py --reset_epoch True --checkpoint "$cp" --hyper_parameters generated_switching_cherokee6d --accumulation_size 2

date