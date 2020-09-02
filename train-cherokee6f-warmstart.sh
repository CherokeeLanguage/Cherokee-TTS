#!/bin/bash -x
set -e
set -o pipefail
clear

cd "$(dirname "$0")"
WORK="$(pwd)"

cp="CHEROKEE6E-WARMSTART"

cp "./data/cherokee6f/checkpoint/GENERATED-SWITCHING-CHEROKEE6E_loss-272-0.261" "checkpoints/$cp"

cd data
python prepare_cherokee_spectrograms.py --cherokee_directory cherokee6f

cd "$WORK"
printf "Using checkpoint: $cp\n"

date

export PYTHONIOENCODING=utf-8
python train-ga.py --loader_workers 8 --logging_start 0 --reset_epoch True --checkpoint "$cp" --hyper_parameters generated_switching_cherokee6f --accumulation_size 4

date