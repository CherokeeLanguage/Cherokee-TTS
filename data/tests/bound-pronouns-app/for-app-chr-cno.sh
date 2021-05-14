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

#cp="cherokee5c_loss-185-0.118"
#cp="cherokee5b_loss-300-0.119"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
cp /dev/null "$tmp"

# v=("cno-f-chr_2" "cno-m-chr_2" "cno-m-chr_1" "cno-f-chr_5" "cno-f-chr_3" "cno-f-chr_1")
v=("cno-m-chr_2")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

source_text="$z/review-sheet.txt"
text="$z/tmp-cherokee-tts.txt"
wg="bound-pronouns-app"

tail -n +2 "$source_text" > "$text"

#head -n 3 "$source_text" > "$text"

for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"
	syn=""
	cp /dev/null "$tmp"
	ix=0
	cat "$text" | cut -f 8 -d '|'| uconv -x any-nfd | while read sentence; do
		ix=$(($ix+1))
		printf "%d|%s|%s|chr\n" "$ix" "${sentence}." "$voice" >> "$tmp"
	done

	cd "$y"
	
	cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" --cpu

	cd "$z"
	
	rm -r "$wg"-"$voice" 2> /dev/null || true
	mkdir "$wg"-"$voice"
	cp -p "$text" "$wg"-"$voice"

	rm -r gl-"$wg"-"$voice" 2> /dev/null || true
	mkdir gl-"$wg"-"$voice"
	cp -p "$text" gl-"$wg"-"$voice"

	# python wavernnx.py || 
	python wavernnx-cpu.py
	
	ix=0
	cat "$text" | cut -f 7,8,9 -d '|' | while read phrase; do
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

		wav="$ix.wav"
		mp3=gl-"$wg"-"$voice/$wg-$voice-$iy".mp3
		txt=gl-"$wg"-"$voice/$wg-$voice-$iy".txt
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
	cat "$text" | cut -f 10 -d '|' | while read filename; do
		ix=$(($ix+1))
		iy=$(printf "%02d" $ix)
		
		mp3="$wg"-"$voice/$wg-$voice-$iy".mp3
		newMp3="$wg"-"$voice/$filename".mp3
		mv "$mp3" "$newMp3"
		txt="$wg"-"$voice/$wg-$voice-$iy".txt
		rm "$txt"

		mp3=gl-"$wg"-"$voice/$wg-$voice-$iy".mp3
		newMp3=gl-"$wg"-"$voice/$filename".mp3
		mv "$mp3" "$newMp3"
		txt=gl-"$wg"-"$voice/$wg-$voice-$iy".txt
		rm "$txt"
	done

	xdg-open "$wg"-"$voice"
	
	printf "\n\n"
done

