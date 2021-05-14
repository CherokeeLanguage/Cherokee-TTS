#!/bin/bash -i

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

conda activate Cherokee-TTS

cp="$(ls -1tr checkpoints/*|tail -n 1)"
cp="$(basename "$cp")"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
selected="$z/selected.txt"
cp /dev/null "$tmp"

cp /dev/null "$z"/voices.txt

wg="osiyo-then"
for x in "$z"/"$wg"-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done


#v=("10-chr" "03-chr" "tac-chr_3" "tac-chr_0" "cno-f-chr_2" "02-chr" "cno-m-chr_2" "09-chr" "tac-chr_1" "04-chr" "tac-chr_2" "01-chr" "cno-m-chr_1" "cno-f-chr_5" "cno-f-chr_3" "05-chr" "08-chr" "cno-f-chr_1")
#v=("cno-spk_0")
v=("360-en-m" "329-en-f" "361-en-f" "308-en-f" "311-en-m" "334-en-m")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

text="$z/osiyo-tohiju-then-what.txt"

cat "$text" > "$selected"

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
	
	#python wavernnx.py || 
	python wavernnx-cpu.py

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
	
	count=$(wc -l "$selected"|cut -f 1 -d ' ')
	for ix in $(seq 1 $count); do
		rm "$ix".wav 2> /dev/null || true
		rm "$ix".npy 2> /dev/null || true
	done
	printf "\n\n"
done
