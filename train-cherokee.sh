#!/bin/bash -x
set -e
set -o pipefail
clear

python train-ga.py --hyper_parameters generated_switching_cherokee --accumulation_size 10
