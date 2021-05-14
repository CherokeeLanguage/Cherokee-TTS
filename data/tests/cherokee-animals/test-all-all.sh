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

v=("360-en-m" "329-en-f" "361-en-f" "308-en-f" "311-en-m" "334-en-m" "362-en-f" "330-en-f" "339-en-f" "294-en-f" "310-en-f" "318-en-f" "333-en-f" "305-en-f" "297-en-f" "301-en-f" "341-en-f" "299-en-f" "300-en-f" "345-en-m" "306-en-f" "cno-f-chr_2" "02-chr" "cno-m-chr_2" "09-chr" "04-chr" "01-chr" "cno-m-chr_1" "cno-f-chr_5" "cno-f-chr_3" "05-chr" "08-chr" "cno-f-chr_1")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

wg="animals"
text="$z/animals-game-mco.txt"

cat "$text" | uconv -x any-nfd > "$selected"

for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"
	ix=0
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
	# shellcheck disable=SC2207
	mp3s=($(cut -d "|" -f 3 "$selected" | sed 's/ /_/g'))
	for mp3 in "${mp3s[@]}"; do
		ix="$(($ix+1))"
		wav="wg-$ix.wav"
		mp3="$wg"-"$voice/$voice-$wg-$mp3"
		ffmpeg -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" > /dev/null 2> /dev/null < /dev/null
		rm "$wav"
	done
	
	xdg-open "$wg"-"$voice"
	
	ix=0
	# shellcheck disable=SC2034
	cat "$selected" | while read line; do
		ix="$(($ix+1))"
		rm "$ix".wav 2> /dev/null || true
		rm "$ix".npy 2> /dev/null || true
	done
	printf "\n\n"
done
