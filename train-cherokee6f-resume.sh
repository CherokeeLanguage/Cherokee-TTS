#!/bin/bash -x
set -e
set -o pipefail
clear

params="cherokee6f"
#cp="GENERATED-SWITCHING-CHEROKEE6F_loss-44-0.226"
cp="GENERATED-SWITCHING-CHEROKEE6F_loss-52-0.154"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --accumulation_size 4 --checkpoint "$cp"

date