#!/bin/bash -i

set -e
set -o pipefail

trap "echo ERROR" ERR

cd "$(dirname "$0")"
z="$(pwd)"

conda activate Cherokee-TTS

WAV="$1"
TEXT="$2"

if [ -z "$WAV" ]; then
	echo "Wave file argument not supplied"
	exit 1
fi

if [ -z "$TEXT" ]; then
	echo "Text file argument not supplied"
	exit 1
fi

cp="$(ls -1tr checkpoints/*|tail -n 1)"
cp="$(basename "$cp")"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
cp /dev/null "$tmp"

v=("cno-spk_3" "cno-spk_0")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

wg="tts"

echo "$TEXT" > "$selected"

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
	
	python wavernnx.py || python wavernnx-cpu.py
	
	ix=0
	mp3s=($(cut -f 3 "$selected" | sed 's/ /_/g'))
	for mp3name in "${mp3s[@]}"; do
		ix="$(($ix+1))"
		wav="wg-$ix.wav"
		mp3="$wg"-"$voice/$voice-$wg-$mp3name"
		ffmpeg -y -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" > /dev/null 2> /dev/null < /dev/null
		rm "$wav"
		wav="$ix.wav"
		mp3="$wg"-"$voice/griffin-lim-$voice-$wg-$mp3name"
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

