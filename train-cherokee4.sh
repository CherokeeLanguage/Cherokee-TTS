#!/bin/bash -x
set -e
set -o pipefail
clear

date

export PYTHONIOENCODING=utf-8

python train-ga.py --hyper_parameters generated_switching_cherokee4 --accumulation_size 2

date