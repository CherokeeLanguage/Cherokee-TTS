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

cp="$(ls -1tr checkpoints/|tail -n 1)"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
selected="$z/selected.txt"
cp /dev/null "$tmp"

cp /dev/null "$z"/voices.txt

#shuf "$z"/all-voices.txt | grep 'de' | tail -n 2 >> "$z"/voices.txt
cat "$z"/all-voices.txt | grep 'fr' | sort | uniq >> "$z"/voices.txt
#shuf "$z"/all-voices.txt | grep 'nl' | tail -n 2 >> "$z"/voices.txt

for x in "$z"/ced-[0-9][0-9]-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

v=($(cat "$z"/voices.txt))
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

wg="ced"
text="$z/../../cherokee-syn/syn-chr.txt"

for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"
	cut -f 7 -d '|' "$text" | grep -v ' ' | shuf | tail -n 5 > "$selected"
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
	
	python wavernnx.py

	mv wg*.wav "$wg"-"$voice"/
	xdg-open "$wg"-"$voice"
	
	ix=0
	cat "$selected" | while read line; do
		ix="$(($ix+1))"
		rm "$ix".wav || true
		rm "$ix".npy || true
	done
	printf "\n\n"
done
