#!/bin/bash -x
set -e
set -o pipefail
clear

cd "$(dirname "$0")"

cp="$(ls -1tr checkpoints/|tail -n 1)"
cp="$(basename "$cp")"

printf "Using checkpoint: $cp\n"

date

export PYTHONIOENCODING=utf-8
python train-ga.py --checkpoint "$cp" --accumulation_size 4

date