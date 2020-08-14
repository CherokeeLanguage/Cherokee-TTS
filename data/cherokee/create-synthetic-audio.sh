#!/bin/bash
set -e
set -o pipefail
set -u

trap "echo ERROR" ERR

cd "$(dirname "$0")"
HERE="$(pwd)"

chr="./ced.tsv"
espeakng="${HOME}/espeak-ng/bin/espeak-ng"
WAV="./wav"
CHEROKEE="./cherokee.txt"

IPA="" #global variable
ipa(){
    SAMPA="$1"
    IPA=$SAMPA
    
    #IPA=${IPA//43/˦˧}
    #strip out the word vowel final high fall, should be learned as a general feature of the language
    IPA=${IPA//43/} 
    #tones!
    IPA=${IPA//1/˨˩}
    IPA=${IPA//2/˨}
    IPA=${IPA//3/˧}
    IPA=${IPA//4/˧˦}

    #stress
    IPA=${IPA//\'/ˈ}
    #length
    IPA=${IPA//:/ː}

    IPA=${IPA//\?/ʔ}
    IPA=${IPA//tS/tʃ}
    IPA=${IPA//dZ/dʒ}
    IPA=${IPA//l#/ɬ}

    IPA=${IPA//0~/ɒ̃}
    IPA=${IPA//e~/ẽ}
    IPA=${IPA//i~/ĩ}
    IPA=${IPA//o~/õ}
    IPA=${IPA//u~/ũ}
    IPA=${IPA//@~/ə̃}

    IPA=${IPA//0/ɒ}
}

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
for z in 1 2 3 4 5 6 7 8; do
    cut -f 7 ced.tsv | shuf | sed 's/\.$//g' > c"$z".txt
done

echo "Pasting gibberish Cherokee sentences"

cp /dev/null cx.txt

paste -d ' ' c1.txt c2.txt | shuf | tail -n 40 >> cx.txt
paste -d ' ' c3.txt c4.txt c5.txt | shuf | tail -n 40 >> cx.txt
paste -d ' ' c1.txt c2.txt c3.txt c4.txt | shuf | tail -n 40 >> cx.txt
paste -d ' ' c2.txt c3.txt c4.txt c5.txt c6.txt | shuf | tail -n 40 >> cx.txt
paste -d ' ' c3.txt c4.txt c5.txt c6.txt c7.txt c8.txt | shuf | tail -n 40 >> cx.txt

rm c1.txt c2.txt c3.txt c4.txt c5.txt c6.txt c7.txt c8.txt

wavCounter=0;
echo "Creating synthetic Cherokee"
MAX_PER_SYNTH=100

set +o pipefail

shuf "$chr" | cut -f 7 | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read cedtext; do
    #stock male voice
    voice="chr"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -z -v $voice -w "$wavFile" -x "$cedtext")"
    printf "%06d|espk-default|chr|%s|||%s.|%s\n" "$wavCounter" "$wavFile" "$cedtext" "" >> "$CHEROKEE"
done

shuf "$chr" | cut -f 7 | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read cedtext; do
    #female voice "f2"
    voice="chr+f2"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -z -v $voice -w "$wavFile" -x "$cedtext")"
    printf "%06d|espk-f2|chr|%s|||%s.|%s\n" "$wavCounter" "$wavFile" "$cedtext" "" >> "$CHEROKEE"
done

wavCounter=100000

echo "Creating synthetic Cherokee sentences"
shuf cx.txt | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read cedtext; do
    #stock male voice
    voice="chr"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -z -v $voice -w "$wavFile" -x "$cedtext"|tail -n 1)"
    printf "%06d|espk-default|chr|%s|||%s.|%s\n" "$wavCounter" "$wavFile" "$cedtext" "" >> "$CHEROKEE"
done

wavCounter=150000

shuf cx.txt | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read cedtext; do
    #female voice "f2"
    voice="chr+f2"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -z -v $voice -w "$wavFile" -x "$cedtext"|tail -n 1)"
    printf "%06d|espk-f2|chr|%s|||%s.|%s\n" "$wavCounter" "$wavFile" "$cedtext" "" >> "$CHEROKEE"
done

rm cx.txt

cat "$CHEROKEE" > all.tmp

wavCounter=200000

#add in what little 1st person speaker audio I have
cat cherokee-df.txt >> all.tmp

SYNFRENCH="fr-espk.txt"
cp /dev/null "$SYNFRENCH"

#create synthetic data for voice identification
echo "Creating synthetic French (male)"
shuf "fr.txt" | cut -f 5 -d '|' | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read frtext; do
    #stock male voice
    voice="fr"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -s 100 -z -v $voice -w "$wavFile" --ipa "$frtext")"
    printf "%06d|espk-default|french|%s|||%s|%s\n" "$wavCounter" "$wavFile" "$frtext" "" >> "$SYNFRENCH"
done

wavCounter=250000

echo "Creating synthetic French (female)"
shuf "fr.txt" | cut -f 5 -d '|' | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read frtext; do
    #female voice "f2"
    voice="fr+f2"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -s 100 -z -v $voice -w "$wavFile" --ipa "$frtext")"
    printf "%06d|espk-f2|french|%s|||%s|%s\n" "$wavCounter" "$wavFile" "$frtext" "" >> "$SYNFRENCH"
done

tmpFile="fr.txt"
cut -f 1 -d '|' "$tmpFile" > tmp1 #id
cut -f 2 -d '|' "$tmpFile" > tmp2 #speaker
cut -f 3 -d '|' "$tmpFile" > tmp3 #language
cut -f 4 -d '|' "$tmpFile" > tmp4 #source wav
cut -f 5 -d '|' "$tmpFile" > tmp5 #text
cut -f 999 -d '|' "$tmpFile" > blank
paste -d "|" tmp1 tmp2 tmp3 tmp4 blank blank tmp5 blank >> all.tmp 
rm tmp1 tmp2 tmp3 tmp4 tmp5 blank

cat "$SYNFRENCH" >> all.tmp

wavCounter=300000

SYNDUTCH="nl-espk.txt"
cp /dev/null "$SYNDUTCH"
#create synthetic data for voice identification
echo "Creating synthetic Dutch (male)"
shuf "nl.txt" | cut -f 5 -d '|' | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read estext; do
    #stock male voice
    voice="nl"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -s 100 -z -v $voice -w "$wavFile" --ipa "$estext")"
    printf "%06d|espk-default|nl|%s|||%s|%s\n" "$wavCounter" "$wavFile" "$estext" "" >> "$SYNDUTCH"
done

wavCounter=350000

echo "Creating synthetic Dutch (female)"
shuf "nl.txt" | cut -f 5 -d '|' | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read estext; do
    #female voice "f2"
    voice="nl+f2"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -s 100 -z -v $voice -w "$wavFile" --ipa "$estext")"
    printf "%06d|espk-f2|nl|%s|||%s|%s\n" "$wavCounter" "$wavFile" "$estext" "" >> "$SYNDUTCH"
done

tmpFile="fr.txt"
cut -f 1 -d '|' "$tmpFile" > tmp1 #id
cut -f 2 -d '|' "$tmpFile" > tmp2 #speaker
cut -f 3 -d '|' "$tmpFile" > tmp3 #language
cut -f 4 -d '|' "$tmpFile" > tmp4 #source wav
cut -f 5 -d '|' "$tmpFile" > tmp5 #text
cut -f 999 -d '|' "$tmpFile" > blank
paste -d "|" tmp1 tmp2 tmp3 tmp4 blank blank tmp5 blank >> all.tmp 
rm tmp1 tmp2 tmp3 tmp4 tmp5 blank

#cat "$SYNDUTCH" >> all.tmp

set -o pipefail

shuf all.tmp > all.txt
rm all.tmp

echo "Creating train.txt and val.txt"

split -l $[ $(wc -l all.txt|cut -d " " -f1) * 90 / 100 ] all.txt

mv -v xaa train.txt
mv -v xab val.txt

echo "Done"