#!/bin/bash -x

set -e
set -o pipefail

cd "$(dirname "$0")"

rm -r ma-tracks 2>/dev/null || true
mkdir ma-tracks

echo "=== MP3 -> WAV and TRIM"
for x in ma-tracks.mp3/Track*.mp3; do
	y="$(basename "$x"|sed 's/.mp3/.wav/g')"
	ffmpeg -y -i "${x}" -ar 22050 -ac 1 ma-tracks/tmp.wav || true
	sox ma-tracks/tmp.wav "ma-tracks/${y}" silence 1 0.05 0.1% reverse silence 1 0.05 0.1% reverse || true
	rm ma-tracks/tmp.wav 2> /dev/null || true
done

echo "=== Remove empty files"
for x in ma-tracks/*.wav; do
	size=$(stat --format=%s "$x")
	if [ "$size" = 44 ]; then
		rm -v "$x"
	fi
done

echo "=== Normalize"
for x in ma-tracks/*.wav; do
	sox "$x" "${x}-n.wav" norm -0.1
	mv "${x}-n.wav" "$x"
done

export LC_ALL=C.UTF_8
echo "=== Create ma-tracks.txt"
wavCounter=101000
cp /dev/null ma-tracks.txt
for wavFile in ma-tracks/*.wav; do
	wavCounter=$(($wavCounter + 1))
	printf "%06d|durbin-feeling|chr|%s|||%s.|%s\n" "$wavCounter" "$wavFile" "" "" >> ma-tracks.txt
done
