#!/bin/bash

set -e
set -o pipefail

cd "$(dirname "$0")"
z="$(pwd)"

rm *.npy 2> /dev/null || true
rm *.wav 2> /dev/null || true

cd ../../..
y="$(pwd)"

source ~/miniconda3/etc/profile.d/conda.sh

conda activate ./env

cp="$(ls -1tr checkpoints/*|tail -n 1)"
cp="$(basename "$cp")"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
selected="$z/selected.txt"
cp /dev/null "$tmp"

cp /dev/null "$z"/voices.txt

wg="bc"
for x in "$z"/"$wg"-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

v=("04-chr")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

text="$z/for-audio-quality-vote.txt"

cp "$text" "$selected"

for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"
	syn=""
	cp /dev/null "$tmp"
	ix=0
	cat "$selected" | while read phrase; do
		ix=$(($ix+1))
		printf "%d|%s|%s|chr\n" "$ix" "${phrase}" "$voice" >> "$tmp"
	done

	cd "$y"
	
	cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" --cpu

	cd "$z"
	
	rm -r "$wg"-"$voice" 2> /dev/null || true
	mkdir "$wg"-"$voice"
	cp -p "$selected" "$wg"-"$voice"
	
	python wavernnx.py || python wavernnx-cpu.py

	ix=0
	cat "$selected" | while read phrase; do
		ix=$(($ix+1))
		iy=$(printf "%02d" $ix)
		wav="$wg"-"$voice/wg-$ix.wav"
		mv "wg-$ix.wav" "$wav"
		mp3="$wg"-"$voice/$wg-$voice-$iy".mp3
		txt="$wg"-"$voice/$wg-$voice-$iy".txt
		echo "$phrase" > "$txt"
		normalize-audio -q "$wav"
		ffmpeg -y -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" > /dev/null 2> /dev/null < /dev/null
		rm "$wav"
	done
	
	xdg-open "$wg"-"$voice"
	
	ix=0
	cat "$selected" | while read phrase; do
		ix=$(($ix+1))
		rm "$ix".wav 2> /dev/null || true
		rm "$ix".npy 2> /dev/null || true
	done
	printf "\n\n"
done
