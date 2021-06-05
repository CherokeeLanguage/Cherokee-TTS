#!/usr/bin/env -S conda run -n Cherokee-TTS bash

set -e
set -o pipefail

z="$(pwd)"
cd "$(dirname "$0")"
y="$(pwd)"
cd "$z"

python "$y/tts.py" "$@"

cd "$z"
exit 0
