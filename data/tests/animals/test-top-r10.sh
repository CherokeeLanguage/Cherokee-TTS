#!/bin/bash -i

set -e
set -o pipefail

cd "$(dirname "$0")"
z="$(pwd)"

rm *.npy 2> /dev/null || true
rm *.wav 2> /dev/null || true

for x in "$z"/animals-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

cd ../../..
y="$(pwd)"

conda activate Cherokee-TTS

cp="$(ls -1tr checkpoints/*|tail -n 1)"
cp="$(basename "$cp")"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
selected="$z/selected.txt"
cp /dev/null "$tmp"

cp /dev/null "$z"/voices.txt

for x in "$z"/animals-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

#v=("cno-spk_0" "cno-spk_3" "cno-spk_1" "cno-spk_2" "04-chr" "10-chr")
#v=("cno-spk_0" "cno-spk_1" "cno-spk_2" "cno-spk_3")

#10 top voices based on sample count that aren't chr
#v=('02-ru' '04-fr' '05-ru' '27-de' '11-fr' '08-nl' '01-nl' '04-ru' '52-de' '36-de')

#3 top voices based on sample count that aren't chr
v=('02-ru' '04-fr' '05-ru')

vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

wg="animals"
text="$z/animals-game-mco.txt"

shuf "$text" | uconv -x any-nfd | tail -n 10 > "$selected"

for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"
	ix=0
	syn=""
	cp /dev/null "$tmp"
	cut -d "|" -f 2 "$selected" | while read phrase; do
		ix=$(($ix+1))
		printf "%d|%s|%s|chr\n" "$ix" "${phrase}" "$voice" >> "$tmp"
	done

	cd "$y"
	
	cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" --cpu

	cd "$z"
	
	rm -r "$wg"-"$voice" 2> /dev/null || true
	mkdir "$wg"-"$voice"
	cp -p "$selected" "$wg"-"$voice"
	
	#python wavernnx.py || 
	python wavernnx-cpu.py
	
	ix=0
	mp3s=($(cut -d "|" -f 3 "$selected" | sed 's/ /_/g'))
	for mp3 in "${mp3s[@]}"; do
		ix="$(($ix+1))"
		wav="wg-$ix.wav"
		mp3="$wg"-"$voice/$voice-$wg-$mp3"
		normalize-audio -q "$wav"
		ffmpeg -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" > /dev/null 2> /dev/null < /dev/null
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
