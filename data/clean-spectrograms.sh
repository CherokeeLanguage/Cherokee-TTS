#!/bin/bash

cd "$(dirname "$0")"

for x in *; do
	a="$x"/lin_spectrograms
	if [ -d "$a" ]; then
		echo "$a"
		rm -r "$a"
	fi
	a="$x"/mel_spectrograms
	if [ -d "$a" ]; then
		echo "$a"
		rm -r "$a"
	fi
done