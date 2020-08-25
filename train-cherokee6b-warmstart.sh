#!/bin/bash -x
set -e
set -o pipefail
clear

cd "$(dirname "$0")"
WORK="$(pwd)"

cp "./data/cherokee6b/checkpoint/GENERATED-SWITCHING-CHEROKEE6_loss-230-0.245" "checkpoints/CHEROKEE6B-WARMSTART"
cp="CHEROKEE6B-WARMSTART"

cd data
python prepare_cherokee_spectrograms.py --cherokee_directory cherokee6b

cd "$WORK"
printf "Using checkpoint: $cp\n"

date

export PYTHONIOENCODING=utf-8
python train-ga.py --reset_epoch True --checkpoint "$cp" --hyper_parameters generated_switching_cherokee6b --accumulation_size 5

date