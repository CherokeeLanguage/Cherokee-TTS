#!/bin/bash

set -e
set -o pipefail

trap "echo ERROR" ERR

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

selected="$z/selected.txt"

tmp="$z/tmp.txt"
cp /dev/null "$tmp"

for x in "$z"/flat-[0-9][0-9]-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

v=("cno-spk_0" "cno-spk_1" "cno-spk_2" "cno-spk_3" "09-chr" "08-chr" "05-chr" "04-chr" "03-chr" "02-chr" "01-chr")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

wg="flat"
text="$z/../../cherokee-flat/scripts/script-bare-1.txt"

cat "$text" > "$selected"

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
	
	#python wavernnx-cpu.py
	python wavernnx.py
	

	count=$(wc -l "$selected"|cut -f 1 -d ' ')
	for ix in $(seq 1 $count); do
		iy=$(printf "%02d" $ix)
		wav="$wg"-"$voice/wg-$ix.wav"
		mv "$ix.wav" "$wav"
		mp3="$wg"-"$voice/$wg-$voice-$iy".mp3
		ffmpeg -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" 2>&1 > /dev/null
		rm "$wav"
	done
	
	xdg-open "$wg"-"$voice"
	
	ix=0
	cat "$selected" | while read line; do
		ix="$(($ix+1))"
		rm "$ix".wav 2> /dev/null || true
		rm "$ix".npy 2> /dev/null || true
	done
	printf "\n\n"
done
