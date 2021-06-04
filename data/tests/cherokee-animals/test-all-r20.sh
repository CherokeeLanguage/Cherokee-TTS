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

#all voices sorted by entry count descending
#v=("02-ru" "04-fr" "05-ru" "27-de" "11-fr" "08-nl" "01-nl" "04-ru" "52-de" "36-de" "24-de" "03-nl" "13-de" "21-fr" "19-fr" "20-fr" "16-fr" "37-de" "06-ru" "22-de" "49-de" "07-fr" "14-de" "45-de" "06-fr" "51-de" "41-de" "25-fr" "21-de" "17-de" "47-de" "50-de" "08-fr" "03-ru" "12-de" "07-de" "06-nl" "40-de" "06-de" "09-nl" "48-de" "01-ru" "17-fr" "04-nl" "14-fr" "18-fr" "32-de" "01-de" "01-fr" "10-nl" "12-nl" "02-fr" "43-de" "10-fr" "05-fr" "11-nl" "13-fr" "26-de" "46-de" "02-de" "02-nl" "26-fr" "29-de" "22-fr" "19-de" "33-de" "31-de" "09-fr" "25-de" "09-de" "44-de" "11-de" "15-fr" "07-nl" "05-de" "10-de" "23-de" "04-de")
v=("02-ru" "03-chr" "tac-chr_3" "04-fr" "05-ru" "tac-chr_0" "01-chr" "27-de" "11-fr" "08-nl" "cno-f-chr_2" "01-nl" "04-ru" "52-de" "36-de" "24-de" "03-nl" "02-chr" "13-de" "21-fr" "19-fr" "20-fr" "cno-m-chr_2" "16-fr" "tac-chr_1" "37-de" "06-ru" "22-de" "49-de" "07-fr" "04-chr" "14-de" "45-de" "06-fr" "51-de" "41-de" "25-fr" "tac-chr_2" "21-de" "17-de" "47-de" "50-de" "08-fr" "03-ru" "12-de" "07-de" "06-nl" "40-de" "06-de" "cno-m-chr_1" "09-nl" "cno-f-chr_5" "48-de" "01-ru" "17-fr" "04-nl" "14-fr" "18-fr" "32-de" "01-de" "01-fr" "10-nl" "12-nl" "02-fr" "43-de" "10-fr" "05-fr" "11-nl" "13-fr" "cno-f-chr_3" "26-de" "46-de" "02-de" "02-nl" "26-fr" "29-de" "05-chr" "22-fr" "19-de" "33-de" "31-de" "09-fr" "25-de" "09-de" "44-de" "11-de" "15-fr" "07-nl" "05-de" "10-de" "23-de" "cno-f-chr_1" "04-de")
vsize="${#v[@]}"

printf "\nTotal voice count: %d\n\n" "$vsize"

wg="animals"
text="$z/animals-game-mco.txt"

shuf "$text" | uconv -x any-nfd | tail -n 20 > "$selected"

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
		normalize-audio -q "$wav"
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
