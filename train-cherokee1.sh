#!/bin/bash -x
set -e
set -o pipefail
clear

date

export PYTHONIOENCODING=utf-8

python train-ga.py --hyper_parameters chr --accumulation_size 12

date