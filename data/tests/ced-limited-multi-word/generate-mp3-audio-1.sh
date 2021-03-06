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
selected="$z/for-audio-quality-vote.txt"
cp /dev/null "$tmp"

cp /dev/null "$z"/voices.txt

wg="ced-limited-multi-word-1"
for x in "$z"/"$wg"-*; do
	if [ ! -d "$x" ]; then continue; fi
	rm -r "$x"
done

v=("04-chr" "cno-spk_0" "cno-spk_1" "cno-spk_2" "cno-spk_3")

vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

text="$z/scripts/script-bare-1.txt"

cat "$text" | sort > "$selected"

voiceIdx=0

	#printf "Generating audio for %s\n" "$voice"
	syn=""
	cp /dev/null "$tmp"
	ix=0
	cat "$selected" | cut -f 1 -d '|' | while read phrase; do
		voice="${v[$voiceIdx]}"
		ix=$(($ix+1))
		printf "%d|%s|%s|chr\n" "$ix" "${phrase}" "$voice" >> "$tmp"
		voiceIdx=$((($voiceIdx+1)%$vsize))
	done

	cd "$y"
	
	cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" --cpu

	cd "$z"
	
	rm -r "$wg"-"audio" 2> /dev/null || true
	mkdir "$wg"-"audio"
	cp -p "$selected" "$wg"-"audio"
	
	python wavernnx.py || python wavernnx-cpu.py

	ix=0
	cat "$tmp" | while read line; do
		voice=$(echo "$line"|cut -f 3 -d '|')
		phrase=$(echo "$line"|cut -f 2 -d '|')
		ix=$(($ix+1))
		iy=$(printf "%02d" $ix)
		wav="$wg"-"audio/${wg}_${ix}.wav"
		mv "wg-${ix}.wav" "$wav"
		mp3="$wg"-"audio/${wg}_${voice}_${iy}".mp3
		txt="$wg"-"audio/${wg}_${voice}_${iy}".txt
		echo "$phrase [$voice] | Random dictionary entry(ies)" > "$txt"
		normalize-audio -q "$wav"
		ffmpeg -y -i "$wav" -codec:a libmp3lame -qscale:a 4 "$mp3" > /dev/null 2> /dev/null < /dev/null
		rm "$wav"
	done
	
	xdg-open "$wg"-"audio"
	
	ix=0
	cat "$selected" | while read phrase; do
		ix=$(($ix+1))
		rm "$ix".wav 2> /dev/null || true
		rm "$ix".npy 2> /dev/null || true
	done
	printf "\n\n"
#done
