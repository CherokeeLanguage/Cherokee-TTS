#!/bin/bash -x
set -e
set -o pipefail
clear

params="cherokee6h"
cp="CHEROKEE6H_loss-44-0.084"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --hyper_parameters "$params" --accumulation_size 6 --checkpoint "$cp" --reset_epoch True

date