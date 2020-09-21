#!/bin/bash -x
set -e
set -o pipefail
clear

params="cherokee6h"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --hyper_parameters "$params" --accumulation_size 6 --logging_start 1

date