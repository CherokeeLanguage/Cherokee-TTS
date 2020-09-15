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

selected="$z/selected.txt"

#v=("02-ru" "03-ru" "14-de" "02-fr" "01-chr" "02-chr" "03-chr" "04-chr" "05-chr")
v=("02-ru" "03-ru" "05-chr" "04-chr" "03-chr" "02-chr" "01-chr")
#v=("14-de" "51-de" "02-fr" "04-fr" "14-fr" "18-fr" "19-fr" "22-fr" "03-ru" "03-chr")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

text="$z/bragging-hunter-mco.txt"

wg="bragging-hunter"


for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"	
	ix=0
	syn=""
	cp /dev/null "$selected"
	head -n 1 "$text" | while read sentence; do
		ix=$(($ix+1))
		printf "%d|%s|%s|chr\n" "$ix" "${sentence}" "$voice" >> "$selected"
	done

	cd "$y"
	
	cat "$selected" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" --cpu

	cd "$z"
	
	rm -r "$wg"-"$voice" 2> /dev/null || true
	mkdir "$wg"-"$voice"
	cp -p "$text" "$wg"-"$voice"

	python wavernnx.py || python wavernnx-cpu.py
	
	xdg-open "$wg"-"$voice"
	
	count=$(wc -l "$text"|cut -f 1 -d ' ')
	for ix in $(seq 1 $count); do
		iy=$(printf "%02d" $ix)
		wav="$wg"-"$voice/$voice-$wg-$ix.wav"
		if [ ! -f "wg-$ix.wav" ]; then continue; fi
		mv "wg-$ix.wav" "$wav"
		mp3="$wg"-"$voice/$wg-$voice-$iy".mp3
		ffmpeg -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" > /dev/null 2>&1
		rm "$wav"
	done
	
	count=$(wc -l "$text"|cut -f 1 -d ' ')
	for ix in $(seq 1 $count); do
		ix="$(($ix+1))"
		rm "$ix".wav 2> /dev/null || true
		rm "$ix".npy 2> /dev/null || true
	done
	printf "\n\n"
done

