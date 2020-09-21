#!/bin/bash -x
set -e
set -o pipefail
clear

params="cherokee6g"
cp="CHEROKEE6G_loss-108-0.066"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --accumulation_size 4 --checkpoint "$cp" --logging_start 0

date