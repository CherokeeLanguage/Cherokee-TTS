#!/bin/bash -i
set -e
set -o pipefail
clear

conda activate Cherokee-TTS

params="cherokee5i"
# cp="5h-20210409_loss-35-0.125"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --hyper_parameters "$params" --accumulation_size 3

date