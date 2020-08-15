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

paste -d ' ' c1.txt c2.txt | tail -n 40 >> cx.txt
paste -d ' ' c3.txt c4.txt c5.txt | tail -n 40 >> cx.txt
paste -d ' ' c1.txt c2.txt c3.txt c4.txt | tail -n 40 >> cx.txt
paste -d ' ' c2.txt c3.txt c4.txt c5.txt c6.txt | tail -n 40 >> cx.txt
paste -d ' ' c3.txt c4.txt c5.txt c6.txt c7.txt c8.txt | tail -n 40 >> cx.txt

paste -d ' ' d1.txt d2.txt | tail -n 40 >> dx.txt
paste -d ' ' d3.txt d4.txt d5.txt | tail -n 40 >> dx.txt
paste -d ' ' d1.txt d2.txt d3.txt d4.txt | tail -n 40 >> dx.txt
paste -d ' ' d2.txt d3.txt d4.txt d5.txt d6.txt | tail -n 40 >> dx.txt
paste -d ' ' d3.txt d4.txt d5.txt d6.txt d7.txt d8.txt | tail -n 40 >> dx.txt

rm c1.txt c2.txt c3.txt c4.txt c5.txt c6.txt c7.txt c8.txt
rm d1.txt d2.txt d3.txt d4.txt d5.txt d6.txt d7.txt d8.txt

wavCounter=0;
echo "Creating synthetic Cherokee"
MAX_PER_SYNTH=15

set +o pipefail

wtmp1=wavs.tmp
wtmp2=counters.tmp
wtmp3=blanks.tmp
wtmp4=voice.tmp
wtmp5=language.tmp
wtmp6=text.tmp

cp /dev/null "$wtmp1"
cp /dev/null "$wtmp2"
cp /dev/null "$wtmp3"
cp /dev/null "$wtmp4"
cp /dev/null "$wtmp5"
cp /dev/null "$wtmp6"

if [ 0 = 1 ]; then
	shuf "$chr" > tmp.txt
	wavCounter="0"
	cut -f 1 -d '|' tmp.txt | tail -n $MAX_PER_SYNTH | while read cedtext; do
	    #stock male voice
	    voice="chr"
	    wavCounter=$(($wavCounter + 1))
	    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
	    phonemes="$($espeakng -z -v $voice -w "$wavFile" -x "$cedtext")"
	    printf "%s\n" "$wavFile" >> "$wtmp1"
	    printf "%06d\n" "$wavCounter" >> "$wtmp2"
	    printf "\n" >> "$wtmp3"
	    printf "espk-default\n" >> "$wtmp4"
	    printf "chr\n" >> "$wtmp5"
	done
	cut -f 2 -d '|' tmp.txt | tail -n $MAX_PER_SYNTH > "$wtmp6"
	
	paste -d '|' "$wtmp2" "$wtmp4" "$wtmp5" "$wtmp1" "$wtmp3" "$wtmp3" "$wtmp6" "$wtmp3" >> "$CHEROKEE"
	
	cp /dev/null "$wtmp1"
	cp /dev/null "$wtmp2"
	cp /dev/null "$wtmp3"
	cp /dev/null "$wtmp4"
	cp /dev/null "$wtmp5"
	cp /dev/null "$wtmp6"
fi


if [ 0 = 1 ]; then
	shuf "$chr" > tmp.txt
	wavCounter="$((wavCounter + $MAX_PER_SYNTH))"
	cut -f 1 -d '|' tmp.txt | tail -n $MAX_PER_SYNTH | while read cedtext; do
	    #female voice: f2
	    voice="chr+f2"
	    wavCounter=$(($wavCounter + 1))
	    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
	    phonemes="$($espeakng -z -v $voice -w "$wavFile" -x "$cedtext")"
	    printf "%s\n" "$wavFile" >> "$wtmp1"
	    printf "%06d\n" "$wavCounter" >> "$wtmp2"
	    printf "\n" >> "$wtmp3"
	    printf "espk-f2\n" >> "$wtmp4"
	    printf "chr\n" >> "$wtmp5"
	done
	cut -f 2 -d '|' tmp.txt | tail -n $MAX_PER_SYNTH > "$wtmp6"
	
	paste -d '|' "$wtmp2" "$wtmp4" "$wtmp5" "$wtmp1" "$wtmp3" "$wtmp3" "$wtmp6" "$wtmp3" >> "$CHEROKEE"
fi
wavCounter=100000

if [ 0 = 1 ]; then
	echo "Creating synthetic Cherokee sentences"
	shuf cx.txt | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read cedtext; do
	    #stock male voice
	    voice="chr"
	    wavCounter=$(($wavCounter + 1))
	    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
	    phonemes="$($espeakng -z -v $voice -w "$wavFile" -x "$cedtext"|tail -n 1)"
	    printf "%06d|espk-default|chr|%s|||%s.|%s\n" "$wavCounter" "$wavFile" "$cedtext" "" >> "$CHEROKEE"
	done
fi

wavCounter=150000

if [ 0 = 1 ]; then
shuf cx.txt | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read cedtext; do
    #female voice "f2"
    voice="chr+f2"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -z -v $voice -w "$wavFile" -x "$cedtext"|tail -n 1)"
    printf "%06d|espk-f2|chr|%s|||%s.|%s\n" "$wavCounter" "$wavFile" "$cedtext" "" >> "$CHEROKEE"
done
fi

rm cx.txt || true

cat "$CHEROKEE" > all.tmp

wavCounter=200000

#add in what little 1st person speaker audio I have
cat cherokee-df.txt >> all.tmp

SYNFRENCH="fr-espk.txt"
cp /dev/null "$SYNFRENCH"

#create synthetic data for voice identification
if [ 0 = 1 ]; then
echo "Creating synthetic French (male)"
shuf "fr.txt" | cut -f 5 -d '|' | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read frtext; do
    #stock male voice
    voice="fr"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -s 100 -z -v $voice -w "$wavFile" --ipa "$frtext")"
    printf "%06d|espk-default|french|%s|||%s|%s\n" "$wavCounter" "$wavFile" "$frtext" "" >> "$SYNFRENCH"
done
fi

wavCounter=250000

if [ 0 = 1 ]; then
echo "Creating synthetic French (female)"
shuf "fr.txt" | cut -f 5 -d '|' | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read frtext; do
    #female voice "f2"
    voice="fr+f2"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -s 100 -z -v $voice -w "$wavFile" --ipa "$frtext")"
    printf "%06d|espk-f2|french|%s|||%s|%s\n" "$wavCounter" "$wavFile" "$frtext" "" >> "$SYNFRENCH"
done
fi

tmpFile="fr.txt"
cut -f 1 -d '|' "$tmpFile" > tmp1 #id
cut -f 2 -d '|' "$tmpFile" > tmp2 #speaker
cut -f 3 -d '|' "$tmpFile" > tmp3 #language
cut -f 4 -d '|' "$tmpFile" > tmp4 #source wav
cut -f 5 -d '|' "$tmpFile" > tmp5 #text
cut -f 999 -d '|' "$tmpFile" > blank
paste -d "|" tmp1 tmp2 tmp3 tmp4 blank blank tmp5 blank >> all.tmp 
rm tmp1 tmp2 tmp3 tmp4 tmp5 blank

#cat "$SYNFRENCH" >> all.tmp

wavCounter=300000

SYNDUTCH="nl-espk.txt"
cp /dev/null "$SYNDUTCH"
if [ 0 = 1 ]; then
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
fi

wavCounter=350000

if [ 0 = 1 ]; then
echo "Creating synthetic Dutch (female)"
shuf "nl.txt" | cut -f 5 -d '|' | egrep -v '^$' | tail -n $MAX_PER_SYNTH | while read estext; do
    #female voice "f2"
    voice="nl+f2"
    wavCounter=$(($wavCounter + 1))
    wavFile="$(printf "%s/%06d.wav" "$WAV" $wavCounter)"
    phonemes="$($espeakng -s 100 -z -v $voice -w "$wavFile" --ipa "$estext")"
    printf "%06d|espk-f2|nl|%s|||%s|%s\n" "$wavCounter" "$wavFile" "$estext" "" >> "$SYNDUTCH"
done
fi

tmpFile="nl.txt"
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