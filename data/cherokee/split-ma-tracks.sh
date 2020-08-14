#!/bin/bash

set -e
set -o pipefail

cd "$(dirname "$0")"

rm -r ma-split 2> /dev/null || true
mkdir ma-split 

echo "=== MP3 -> WAV and SPLIT"
for x in ma-tracks.mp3/Track*.mp3; do
	y="$(basename "$x"|sed 's/.mp3/-.wav/g')"
	ffmpeg -y -i "$x" -ar 22050 -ac 1 ma-split/tmp.wav || true
	sox -V3 ma-split/tmp.wav "ma-split/${y}" silence 1 0.3 0.1% 1 0.3 0.1% : newfile : restart || true
	rm ma-split/tmp.wav 2> /dev/null || true
done

echo "=== Remove empty files"
for x in ma-split/*.wav; do
	size=$(stat --format=%s "$x")
	if [ "$size" = 44 ]; then
		rm -v "$x"
	fi
done

echo "=== Normalize"
for x in ma-split/*.wav; do
	sox "$x" "${x}-n.wav" norm -0.1
	mv "${x}-n.wav" "$x"
done

echo "=== Create ma-split.txt"
wavCounter=100000
cp /dev/null ma-split.txt
for wavFile in ma-split/*.wav; do
	wavCounter=$(($wavCounter + 1))
	printf "%06d|durbin-feeling|chr|%s|||%s.|%s\n" "$wavCounter" "$wavFile" "" "" >> ma-split.txt
done
