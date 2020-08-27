#!/bin/bash -x
set -e
set -o pipefail
clear

cd "$(dirname "$0")"

cp="GENERATED-SWITCHING-CHEROKEE6C_loss-125-0.194"

printf "Using checkpoint: $cp\n"

date

export PYTHONIOENCODING=utf-8
python train-ga.py --checkpoint "$cp" --accumulation_size 2

date