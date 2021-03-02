#!/bin/bash -i

set -e
set -o pipefail

conda activate Cherokee-TTS

z="$(pwd)"
cd "$(dirname "$0")"
y="$(pwd)"
cd "$z"

python "$y/tts.py" "$@"

cd "$z"
exit 0