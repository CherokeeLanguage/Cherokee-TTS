#!/bin/bash -i

set -e
set -o pipefail

cd "$(dirname "$0")"
z="$(pwd)"

rm *.npy 2> /dev/null || true
rm *.wav 2> /dev/null || true

for x in "$z"/bound-pronouns-app-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

cd ../../..
y="$(pwd)"

conda activate Cherokee-TTS

cp="$(ls -1tr checkpoints/|tail -n 1)"
cp="$(basename "$cp")"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
cp /dev/null "$tmp"

#v=("cno-spk_0" "cno-spk_1" "cno-spk_2" "cno-spk_3" "09-chr" "08-chr" "05-chr" "04-chr" "03-chr" "02-chr" "01-chr")
v=("04-chr" "cno-spk_0" "cno-spk_1" "cno-spk_2" "cno-spk_3")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

source_text="$z/cherokee-tts.txt"
text="$z/tmp-cherokee-tts.txt"
wg="bound-pronouns-app"

cp "$source_text" "$text"

head -n 5 "$source_text" > "$text"

for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"
	syn=""
	cp /dev/null "$tmp"
	ix=0
	cat "$text" | cut -f 2 | uconv -x any-nfd | while read sentence; do
		ix=$(($ix+1))
		printf "%d|%s|%s|chr\n" "$ix" "${sentence}." "$voice" >> "$tmp"
	done

	cd "$y"
	
	cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" #--cpu

	cd "$z"
	
	rm -r "$wg"-"$voice" 2> /dev/null || true
	mkdir "$wg"-"$voice"
	cp -p "$text" "$wg"-"$voice"

	python wavernnx.py || python wavernnx-cpu.py
	
	xdg-open "$wg"-"$voice"
	
	ix=0
	cat "$text" | cut -f 1-4 | while read phrase; do
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

	count=$(wc -l "$text"|cut -f 1 -d ' ')
	for ix in $(seq 1 $count); do
		rm "$ix".wav 2> /dev/null || true
		rm "$ix".npy 2> /dev/null || true
	done

	ix=0
	cat "$text" | cut -f 5 | while read filename; do
		ix=$(($ix+1))
		iy=$(printf "%02d" $ix)
		mp3="$wg"-"$voice/$wg-$voice-$iy".mp3
		newMp3="$wg"-"$voice/$filename".mp3
		mv "$mp3" "$newMp3"
		txt="$wg"-"$voice/$wg-$voice-$iy".txt
		newTxt="$wg"-"$voice/$filename".txt
		mv "$txt" "$newTxt"
	done
	
	printf "\n\n"
done

