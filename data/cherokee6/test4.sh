#!/bin/bash

cd "$(dirname "$0")"
z="$(pwd)"

cd ../..

source ~/miniconda3/etc/profile.d/conda.sh

conda activate ./env

cp="$(ls -1tr checkpoints/|tail -n 1)"

printf "Using checkpoint: $cp\n"

#fr="On les a gardés pour que le taulier les voie ce matin."
#fr="Brebis. Mouton."
fr="Mouton."

chr="U:nò:de̋:na."
chrb="U:nò:de̋:na hawi:ya."
chrc="Ná:hnv́ galò:gwé ga:ne̋:hi u:dlv̌:kwsati gè:sé, ale go:hű:sdi yǔ:dv̂:ne̋:la à:dlv̌:kwsgé."

printf "1|%s|01-chr|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

printf "2|%s|12-de|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

printf "3|%s|04-fr|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

printf "4|%s|02-nl|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

printf "5|%s|14-de|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

printf "6|%s|10-fr|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

printf "7|%s|01-chr|chr\n" "$chrc" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

printf "8|%s|01-chr|chr\n" "$chrb" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu	

cd "$z"

python wavernn1.py

xdg-open .

