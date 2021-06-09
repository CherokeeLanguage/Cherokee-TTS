#!/usr/bin/env -S bash

set -e
set -o pipefail

type -P conda || export PATH="${HOME}/miniconda3/bin:${PATH}"

z="$(pwd)"
cd "$(dirname "$0")"
y="$(pwd)"
cd "$z"

"$y/tts.py" "$@"

cd "$z"
exit 0
