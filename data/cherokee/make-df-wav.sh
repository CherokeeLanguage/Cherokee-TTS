#!/bin/bash

cd "$(dirname "$0")"

for x in ma-tracks.mp3/*.mp3; do
    wav="$(basename "$x"|sed 's/.mp3/.wav/g')"
    ffmpeg -y -i "$x" -ar 22050 -ac 1 "ma-tracks/$wav"
done