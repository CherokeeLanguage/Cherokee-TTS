#!/bin/bash
set -e
set -o pipefail
set -u

trap "echo ERROR" ERR

cd "$(dirname "$0")"
HERE="$(pwd)"

chr="./ced-multi.txt"
paste -d '|' ced-ced.tsv ced-mco.tsv > "$chr"

espeakng="${HOME}/espeak-ng/bin/espeak-ng"
WAV="./wav"
CHEROKEE="./syn-chr.txt"

if [ -d "$WAV" ]; then
    rm -rf "$WAV"
fi
mkdir -p "$WAV"

#cleanup from any previous runs
rm -r linear_spectrograms > /dev/null || true
rm -r spectrograms > /dev/null || true

cp /dev/null "$CHEROKEE"

echo "Creating gibberish Cherokee sentences"
#create longer sequences (giberish) to simulate full sentences.
paste -d '|' ced-ced.tsv ced-mco.tsv > tmp.txt
for z in 1 2 3 4 5 6 7 8; do
    shuf tmp.txt > x"$z".txt
    cut -f 1 -d '|' x"$z".txt > c"$z".txt
    cut -f 2 -d '|' x"$z".txt > d"$z".txt
    rm x"$z".txt
done
rm tmp.txt

echo "Pasting gibberish Cherokee sentences"

cp /dev/null cx.txt
cp /dev/null dx.txt

paste -d ' ' c1.txt c2.txt  >> cx.txt
paste -d ' ' c3.txt c4.txt c5.txt  >> cx.txt
paste -d ' ' c1.txt c2.txt c3.txt c4.txt  >> cx.txt
paste -d ' ' c2.txt c3.txt c4.txt c5.txt c6.txt  >> cx.txt
paste -d ' ' c3.txt c4.txt c5.txt c6.txt c7.txt c8.txt  >> cx.txt

paste -d ' ' d1.txt d2.txt  >> dx.txt
paste -d ' ' d3.txt d4.txt d5.txt  >> dx.txt
paste -d ' ' d1.txt d2.txt d3.txt d4.txt  >> dx.txt
paste -d ' ' d2.txt d3.txt d4.txt d5.txt d6.txt  >> dx.txt
paste -d ' ' d3.txt d4.txt d5.txt d6.txt d7.txt d8.txt  >> dx.txt

rm c1.txt c2.txt c3.txt c4.txt c5.txt c6.txt c7.txt c8.txt
rm d1.txt d2.txt d3.txt d4.txt d5.txt d6.txt d7.txt d8.txt

paste -d '|' cx.txt dx.txt > ex.txt

rm cx.txt dx.txt

wavCounter=0;
echo "Creating synthetic Cherokee"
MAX_PER_SYNTH=50

wavCounter=100000
shuf "$chr" | tail -n $MAX_PER_SYNTH > tmp.txt

voice="chr"
cut -f 1 -d '|' tmp.txt | while read cedtext; do
    #if [ $voice = "chr" ]; then
    #	voice="chr+f2"
    #	id="02-syn-chr"
    #else
    	voice="chr"
    	id="01-syn-chr"
    #fi
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    $espeakng -z -v $voice -w "$wavFile" -x "$cedtext"
done

voice="chr"
cut -f 2 -d '|' tmp.txt | while read mcotext; do
	 #if [ $voice = "chr" ]; then
    #	voice="chr+f2"
    #	id="02-syn-chr"
    #else
    	voice="chr"
    	id="01-syn-chr"
    #fi
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    printf "%06d|%s|chr|%s|||%s.|%s\n" "$wavCounter" "$id" "$wavFile" "$mcotext" "" >> "$CHEROKEE"
done

voice="chr"
wavCounter=110000
shuf ex.txt | tail -n $MAX_PER_SYNTH > tmp.txt
cut -f 1 -d '|' tmp.txt | while read cedtext; do
    #if [ $voice = "chr" ]; then
    #	voice="chr+f2"
    #	id="02-syn-chr"
    #else
    	voice="chr"
    	id="01-syn-chr"
    #fi
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    $espeakng -z -v $voice -w "$wavFile" -x "$cedtext"
done

voice="chr"
cut -f 2 -d '|' tmp.txt | while read cedtext; do
    #if [ $voice = "chr" ]; then
    #	voice="chr+f2"
    #	id="02-syn-chr"
    #else
    	voice="chr"
    	id="01-syn-chr"
    #fi
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    printf "%06d|%s|chr|%s|||%s.|%s\n" "$wavCounter" "$id" "$wavFile" "$cedtext" "" >> "$CHEROKEE"
done

rm ex.txt || true

echo "Done"