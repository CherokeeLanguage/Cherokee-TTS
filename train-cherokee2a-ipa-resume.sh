#!/bin/bash -i
set -e
set -o pipefail
clear

conda activate Cherokee-TTS

params="cherokee2a-ipa"
cp="cherokee2a-ipa_loss-25-0.106"
cp="cherokee2a-ipa_loss-35-0.099"
cp="cherokee2a-ipa_loss-45-0.094"

cd "$(dirname "$0")"
WORK="$(pwd)"

#cp -v data/"$params"/checkpoint/"$cp" checkpoints/

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --log_high_loss --hyper_parameters "$params" --checkpoint "$cp" --accumulation_size 2

date