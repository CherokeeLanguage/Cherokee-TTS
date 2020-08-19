#!/bin/bash -x

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

ix=0
syn=""
cut -f 2 "$z/animals-game-mco.tsv" | while read critter; do
	ix=$(($ix+1))
	printf "%d|%s|01-chr|chr\n" "$ix" "${critter}." >> "$tmp"
done

cat "$tmp" | python synthesize.py --output "$z/" --save_spec --checkpoint "checkpoints/$cp" --cpu

xdg-open .

cd "$z"
python wavernnx.py

ix=0
cat "$z/animals-game-mco-tsv" | while read line; do
	ix="$(($ix+1))"
	rm "$ix".wav
	rm "$ix".npy
done

