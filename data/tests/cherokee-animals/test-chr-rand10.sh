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

#cp="$(ls -1tr checkpoints/*CHEROKEE4*|tail -n 1)"
cp="$(ls -1tr checkpoints/*CHEROKEE*|tail -n 1)"
cp="$(basename "$cp")"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
selected="$z/selected.txt"
cp /dev/null "$tmp"

cp /dev/null "$z"/voices.txt

(
	echo "01-chr"
	echo "02-chr"
) >> "$z"/voices.txt

#cat "$z"/all-voices.txt | grep 'fr' | sort | uniq >> "$z"/voices.txt

for x in "$z"/animals-[0-9][0-9]-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

v=($(cat "$z"/voices.txt))
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

wg="animals"
text="$z/animals-game-mco.txt"

cut -f 2 "$text" | shuf | tail -n 10 | sort > "$selected"
	
for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"
	ix=0
	syn=""
	cp /dev/null "$tmp"
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
	
	python wavernnx-cpu.py

	mv wg*.wav "$wg"-"$voice"/
	ix=0
	cut -f 3 "$text" | while read mp3; do
		ix="$(($ix+1))"
		wav="$wg"-"$voice/$ix.wav"
		mp3="$wg"-"$voice/$mp3"
		ffmpeg -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" && rm "$wav"
	done
	
	xdg-open "$wg"-"$voice"
	
	ix=0
	cat "$selected" | while read line; do
		ix="$(($ix+1))"
		rm "$ix".wav || true
		rm "$ix".npy || true
	done
	printf "\n\n"
done