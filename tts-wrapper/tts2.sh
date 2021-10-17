#!/usr/bin/env -S bash

set -e
set -o pipefail

type -P conda || export PATH="${HOME}/miniconda3/bin:${PATH}"

z="$(pwd)"
cd "$(dirname "$0")"
y="$(pwd)"
cd "$z"

conda run --no-capture-output -n Cherokee-TTS python "$y/tts2.py" "$@"

cd "$z"
exit 0
