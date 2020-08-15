#!/bin/bash
set -e
set -o pipefail
set -u

trap "echo ERROR" ERR

cd "$(dirname "$0")"
HERE="$(pwd)"

WAV="./wav"

if [ -d "$WAV" ]; then
    rm -rf "$WAV"
fi
mkdir -p "$WAV"

#cleanup from any previous runs
rm -r linear_spectrograms 2> /dev/null || true
rm -r spectrograms 2> /dev/null || true

cp /dev/null all.tmp

#add in what little 1st person speaker audio I have
cat cherokee-df.txt >> all.tmp

tmpFile="common-voice-clean.txt"
cut -f 1 -d '|' "$tmpFile" > tmp1 #id
cut -f 2 -d '|' "$tmpFile" > tmp2 #speaker
cut -f 3 -d '|' "$tmpFile" > tmp3 #language
cut -f 4 -d '|' "$tmpFile" > tmp4 #source wav
cut -f 5 -d '|' "$tmpFile" > tmp5 #text
cut -f 999 -d '|' "$tmpFile" > blank

paste -d "-" tmp2 tmp3 > tmp6

paste -d "|" tmp1 tmp6 tmp3 tmp4 blank blank tmp5 blank >> all.tmp 
rm tmp? tmp?? blank 2> /dev/null || true

shuf all.tmp > all.txt
rm all.tmp

echo "Creating train.txt and val.txt"

split -l $[ $(wc -l all.txt|cut -d " " -f1) * 90 / 100 ] all.txt

mv -v xaa train.txt
mv -v xab val.txt

echo "Done"