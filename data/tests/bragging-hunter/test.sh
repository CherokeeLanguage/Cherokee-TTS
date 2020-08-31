#!/bin/bash

set -e
set -o pipefail

cd "$(dirname "$0")"
z="$(pwd)"

rm *.npy 2> /dev/null || true
rm *.wav 2> /dev/null || true

for x in "$z"/*-[0-9][0-9]-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

cd ../../..
y="$(pwd)"

source ~/miniconda3/etc/profile.d/conda.sh

conda activate ./env

cp="$(ls -1tr checkpoints/|tail -n 1)"
cp="$(basename "$cp")"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
cp /dev/null "$tmp"

v=("04-chr" "03-chr" "02-chr" "01-chr")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

text="$z/two-hunters-mco.txt"

wg="bragging-hunter"

for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"
	ix=0
	syn=""
	cat "$text" | while read sentence; do
		ix=$(($ix+1))
		printf "%d|%s|%s|chr\n" "$ix" "${sentence}" "$voice" >> "$tmp"
	done

	cd "$y"
	
	cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" --cpu

	cd "$z"
	
	rm -r "$wg"-"$voice" 2> /dev/null || true
	mkdir "$wg"-"$voice"
	cp -p "$text" "$wg"-"$voice"

	python wavernnx-cpu.py
	
	count=$(wc -l "$text")
	for ix in $(seq 1 1 $count); do
		iy=$(($ix - 1))
		mp3=$(printf "%02d" $count)
		wav="wg-$iy.wav"
		mp3="$wg"-"$voice/$mp3"
		ffmpeg -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3"
		rm "$wav"
	done

	xdg-open "$wg"-"$voice"
	
	ix=0
	cat "$text" | while read line; do
		ix="$(($ix+1))"
		rm "$ix".wav
		rm "wg-$ix".wav
		rm "$ix".npy
	done
	printf "\n\n"
done

