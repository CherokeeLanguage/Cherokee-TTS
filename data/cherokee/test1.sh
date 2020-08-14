#!/bin/bash

cd "$(dirname "$0")"

cd ../..

source ~/miniconda3/etc/profile.d/conda.sh

conda activate ./env

cp="$(ls -1tr checkpoints/|tail -n 1)"

printf "Using checkpoint: $cp\n"

#MCS: Ná:hnv́ galò:gwé ga:ne̋:hi u:dlv̌:kwsati gè:sé, ale go:hű:sdi yǔ:dv̂:ne̋:la à:dlv̌:kwsgé.
chr="Na³hnv³ gạ²lo¹gwe³ ga²ne⁴hi u²dlv²³kwsạ²ti ge¹se³, ạ²le go²hu⁴sdi yu²³dv³²ne⁴la a¹dlv²³kwsge³."
#chr="Ụ²wo²³dị³ge⁴ɂi gi²hli a¹ke²³he³²ga na ạ²chu⁴ja."
#chr="Ụ²wo²³dị³ge⁴ɂi."

printf "1|%s|durbin-feeling|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

printf "2|%s|02-fr|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

printf "3|%s|04-fr|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

printf "4|%s|05-fr|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu	

printf "5|%s|06-fr|chr\n" "$chr" | \
	python synthesize.py --save_spec --checkpoint "checkpoints/$cp" #--cpu

xdg-open .