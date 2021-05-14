#!/bin/bash -i

set -e
set -o pipefail

conda activate Cherokee-TTS

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

cp="$(ls -1tr checkpoints/*|tail -n 1)"
cp="$(basename "$cp")"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
selected="$z/selected.txt"
cp /dev/null "$tmp"

cp /dev/null "$z"/voices.txt

wg="osiyo-then"
for x in "$z"/"$wg"-[0-9][0-9]-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

v=(
"01-fr" 
"02-fr" 
"04-fr" 
"05-fr" 
"06-fr" 
"07-fr" 
"08-fr" 
"09-fr" 
"10-fr" 
"11-fr" 
"13-fr" 
"14-fr" 
"15-fr" 
"16-fr" 
"17-fr" 
"18-fr" 
"19-fr" 
"20-fr" 
"21-fr" 
"22-fr" 
"25-fr" 
"26-fr" 
)

vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

text="$z/osiyo-tohiju-then-what.txt"

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
	
	python wavernnx-cpu.py

	count=$(wc -l "$selected"|cut -f 1 -d ' ')
	for ix in $(seq 1 $count); do
		iy=$(printf "%02d" $ix)
		wav="$wg"-"$voice/wg-$ix.wav"
		mv "wg-$ix.wav" "$wav"
		mp3="$wg"-"$voice/$wg-$voice-$iy".mp3
		ffmpeg -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" > /dev/null 2> /dev/null
		rm "$wav"
	done
	
	xdg-open "$wg"-"$voice"
	
	count=$(wc -l "$selected"|cut -f 1 -d ' ')
	for ix in $(seq 1 $count); do
		rm "$ix".wav 2> /dev/null || true
		rm "$ix".npy 2> /dev/null || true
	done
	printf "\n\n"
done
