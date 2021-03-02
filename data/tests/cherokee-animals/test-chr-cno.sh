#!/bin/bash -i

set -e
set -o pipefail

trap "echo ERROR" ERR

conda activate Cherokee-TTS

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

v=("cno-spk_0" "cno-spk_1" "cno-spk_2" "cno-spk_3") # "09-chr" "08-chr" "05-chr" "04-chr" "03-chr" "02-chr" "01-chr")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

wg="animals"
text="$z/animals-game-mco.txt"

cat "$text" | uconv -x any-nfd | sort > "$selected"

for voice in "${v[@]}"; do
	printf "Generating audio for %s\n" "$voice"
	ix=0
	syn=""
	cp /dev/null "$tmp"
	cut -f 2 "$selected" | while read phrase; do
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
	#python wavernnx-cpu.py
	
	ix=0
	cat "$selected" | while read line; do
		ix="$(($ix+1))"

		mp3name="$(echo "$line" | cut -f 3 | sed 's/ /_/g')"
		text="$(echo "$line" | cut -f 2)"
		textname="$(echo "$mp3name" | sed 's/.mp3$/.txt/')"
		
		textFile="$wg"-"$voice/$voice-$wg-$textname"
		echo "$text" > "$textFile"

		#wav="wg-$ix.wav"
		#normalize-audio -q "$wav"
		#mp3="$wg"-"$voice/$voice-$wg-$mp3name"
		#ffmpeg -y -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" > /dev/null 2> /dev/null < /dev/null
		#rm "$wav"
		
		wav="$ix.wav"
		normalize-audio -q "$wav"
		mp3="$wg"-"$voice/gl-$voice-$wg-$mp3name"
		ffmpeg -y -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" > /dev/null 2> /dev/null < /dev/null
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
