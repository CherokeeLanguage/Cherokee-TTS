#!/bin/bash

set -e
set -o pipefail

cd "$(dirname "$0")"
z="$(pwd)"

rm *.npy 2> /dev/null || true
rm *.wav 2> /dev/null || true

cd ../../..

source ~/miniconda3/etc/profile.d/conda.sh

conda activate ./env

cp="$(ls -1tr checkpoints/|tail -n 1)"

printf "Using checkpoint: $cp\n"

#fr="On les a gardés pour que le taulier les voie ce matin."
#fr="Brebis. Mouton."
fr="Mouton."

tmp="$z/tmp.txt"
cp /dev/null "$tmp"

v=( "01-chr" # Cherokee - DF
	"01-syn-chr" # espeak male
	"02-syn-chr" # espeak female
	"14-de" # German - female
	"46-de" # German - male
	"51-de" # German - female
	"22-fr" # French - female *
	"19-fr" # French - female
	"18-fr" # French - female
	"14-fr" # French - female
	"05-fr" # French - male
	"04-fr" # French - female
	"02-fr" # French - female
	"12-nl" # Dutch - male
	)

vmod="${#v[@]}"
vcounter=0

ix=0
syn=""
cut -f 2 "$z/animals-game-mco.tsv" | while read critter; do
	voice="${v[$vcounter]}"
	vcounter=$((($vcounter+1) % $vmod))
	ix=$(($ix+1))
	printf "%d|%s|%s|chr\n" "$ix" "${critter}." "$voice" >> "$tmp"
done

cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" --cpu

rm -r wg 2> /dev/null || true
mkdir wg

xdg-open "$z/"

cd "$z"
python wavernnx.py

mv wg*.wav wg/.

ix=0
cat "$z/animals-game-mco.tsv" | while read line; do
	ix="$(($ix+1))"
	rm "$ix".wav
	rm "$ix".npy
done

