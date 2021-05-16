#!/bin/bash -i
set -e
set -o pipefail
clear

conda activate Cherokee-TTS

params="cherokee2b"
cp="cherokee6i-192-0.216"

cd "$(dirname "$0")"
WORK="$(pwd)"

#cp -v data/"$params"/checkpoint/"$cp" checkpoints/

cd data
python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --hyper_parameters "$params" --accumulation_size 2

date