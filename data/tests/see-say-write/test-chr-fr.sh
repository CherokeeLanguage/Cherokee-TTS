#!/bin/bash -i

set -e
set -o pipefail

cd "$(dirname "$0")"
z="$(pwd)"

rm *.npy 2> /dev/null || true
rm *.wav 2> /dev/null || true

cd ../../..
y="$(pwd)"

conda activate Cherokee-TTS

cp="$(ls -1tr checkpoints/*|tail -n 1)"
cp="$(basename "$cp")"

printf "Using checkpoint: $cp\n"

tmp="$z/tmp.txt"
cp /dev/null "$tmp"

wg="see-say-write"
for x in "$z"/"$wg"-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

v=("01-fr" "02-fr" "04-fr" "05-fr" "06-fr" "07-fr" "08-fr" "09-fr" "10-fr" "11-fr" "13-fr" "14-fr" "15-fr" "16-fr" "17-fr" "18-fr" "19-fr" "20-fr" "21-fr" "22-fr" "25-fr" "26-fr")
vsize="${#v[@]}"

selected="$z/see-say-write-for-audio-quality-vote.txt"

printf "\nTotal voice count: %d\n\n" "$vsize"

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
	
	cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" || \
		cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" --cpu

	cd "$z"
	
	rm -r "$wg"-"$voice" 2> /dev/null || true
	mkdir "$wg"-"$voice"
	cp -p "$selected" "$wg"-"$voice"
	
	python wavernnx.py || python wavernnx-cpu.py

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
