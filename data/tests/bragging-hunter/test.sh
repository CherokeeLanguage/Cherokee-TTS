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

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
cp /dev/null "$tmp"

#v=($(cat "$z"/voices.txt))
v=("08-fr" "26-fr")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

text="$z/two-hunters-mco.txt"

for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"
	ix=0
	syn=""
	cat "$text" | while read sentence; do
		ix=$(($ix+1))
		printf "%d|%s|%s|chr\n" "$ix" "${sentence}" "$voice" >> "$tmp"
	done

	cd "$y"
	
	cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" #--cpu

	cd "$z"
	
	rm -r bragging-hunter-"$voice" 2> /dev/null || true
	mkdir bragging-hunter-"$voice"


	python wavernnx.py

	mv wg*.wav bragging-hunter-"$voice"/
	xdg-open bragging-hunter-"$voice"
	
	ix=0
	cat "$text" | while read line; do
		ix="$(($ix+1))"
		rm "$ix".wav
		rm "$ix".npy
	done
	printf "\n\n"
done

