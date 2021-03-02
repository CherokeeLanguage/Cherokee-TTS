#!/bin/bash -i
set -e
set -o pipefail
clear
conda activate Cherokee-TTS
tensorboard --logdir logs --port 8090
