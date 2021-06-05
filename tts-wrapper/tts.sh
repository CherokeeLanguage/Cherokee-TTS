#!/usr/bin/env bash

set -e
set -o pipefail

z="$(pwd)"
cd "$(dirname "$0")"
y="$(pwd)"
cd "$z"

"$y/tts.py" "$@"

cd "$z"
exit 0
