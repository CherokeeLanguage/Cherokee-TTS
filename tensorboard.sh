#!/bin/bash -x
set -e
set -o pipefail
clear
tensorboard --logdir logs --port 8090
