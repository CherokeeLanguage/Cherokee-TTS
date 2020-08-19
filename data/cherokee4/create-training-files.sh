#!/bin/bash
set -e
set -o pipefail
set -u

trap "echo ERROR" ERR

cd "$(dirname "$0")"
HERE="$(pwd)"

#cleanup from any previous runs
rm -r ../*/linear_spectrograms 2> /dev/null || true
rm -r ../*/spectrograms 2> /dev/null || true

cp /dev/null all.tmp

#add in what little 1st person speaker audio I have
cat ma-split-annotated.txt | sed 's|durbin-feeling|01-chr|' | sed 's|ma-split/|../cherokee/ma-split/|'  >> all.tmp
cat ma-tracks-annotated.txt | sed 's|durbin-feeling|01-chr|' | sed 's|ma-tracks/|../cherokee/ma-tracks/|' >> all.tmp

#syn cherokee
cat ../cherokee-syn/syn-chr.txt | sed 's|./wav/|../cherokee-syn/wav/|' >> all.tmp

comvoi="comvoi-subset.txt"
egrep -vi '^.*?\|.*?\|.*?\|.*?\|.*?v.*?' ../comvoi_clean/all.txt > "$comvoi"

cut -f 1 -d '|' "$comvoi" > tmp1 #id
cut -f 2 -d '|' "$comvoi" > tmp2 #speaker
cut -f 3 -d '|' "$comvoi" > tmp3 #language
cut -f 4 -d '|' "$comvoi" > tmp4 #source wav
cut -f 5 -d '|' "$comvoi" > tmp5 #text
cut -f 999 -d '|' "$comvoi" > blank

#point to the original data the common voice data was pulled from
sed -i 's|^|../comvoi_clean/|' tmp4

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