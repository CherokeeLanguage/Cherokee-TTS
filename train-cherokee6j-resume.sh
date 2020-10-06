#!/bin/bash -x
set -e
set -o pipefail
clear

params="cherokee6j"
cp="cherokee6j_loss-36-0.332"

cd "$(dirname "$0")"
WORK="$(pwd)"

cp -v data/"$params"/checkpoint/"$cp" checkpoints/

#cd data
#python prepare_spectrograms.py --directory "$params"

date

cd "$WORK"
export PYTHONIOENCODING=utf-8
python trainGa.py --checkpoint "$cp" --accumulation_size 5

date