#!/bin/bash -i
set -e
set -o pipefail
clear

conda activate Cherokee-TTS

params="cherokee7a"
#cp="cherokee2a-ipa_loss-20-0.132"

cd "$(dirname "$0")"
WORK="$(pwd)"

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --hyper_parameters "$params" --accumulation_size 4

date