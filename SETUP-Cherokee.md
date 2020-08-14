# Setup

Example steps to run this project

## Get the code

```bash
cd ~/git
git clone git@github.com:CherokeeLanguage/Multilingual_Text_to_Speech.git
```

## Virtual Environment

```bash
cd ~/git/Multilingual_Text_to_Speech
conda create --prefix ./env python=3.7
conda activate ./env
pip install -r requirements.txt
```

## Datasets

```bash
cd ~/git/Multilingual_Text_to_Speech
cd data/css10

cut -f 2 -d '|' val.txt | sort -u | while read l; do
    mkdir "$l"
done

```

### Manually unpack zips into correct folders

The unpacked audio files take up about 86GB of space unpacked before spectrograms and other processing is performed.

## Verify all needed audio files are in place

```bash
cd ~/git/Multilingual_Text_to_Speech
cd data/css_comvoi
cut -f 4 val.txt | while read f; do
    if [ ! -f "$f" ]; then echo "FILE MISSING: $f"; exit -1; fi
done
```

```bash
cd ~/git/Multilingual_Text_to_Speech
cd data/css_comvoi
cut -f 4 train.txt | while read f; do
    if [ ! -f "$f" ]; then echo "FILE MISSING: $f"; exit -1; fi
done
```

## Patch phonemizer

For better fidelity in phonemic transcriptions we need to ensure the phonemizer call has with_stress set to "True".

```diff
--- a/utils/text.py
+++ b/utils/text.py
@@ -88,7 +88,7 @@ def to_phoneme(text, ignore_punctuation, language, phoneme_dictionary=None):
 def _phonemize(text, language):
     try:
         seperators = Separator(word=' ', phone='')
-        phonemes = phonemize(text, separator=seperators, backend='espeak', language=language)           
+        phonemes = phonemize(text, separator=seperators, backend='espeak', with_stress=True, language=language)           
     except RuntimeError:
         epi = epitran.Epitran(language)
         phonemes = epi.transliterate(text, normpunc=True)
```

Prepare spectrograms:

```bash
cd ~/git/Multilingual_Text_to_Speech
conda activate ./env
cd data
python3 prepare_css_spectrograms.py
```

## Adjust hyper params

```bash
cd ~/git/Multilingual_Text_to_Speech
conda activate ./env #only if env is not already active
cd params
cp generated_training.json generated_training_low_memory.json 
code generated_training_low_memory.json 
```

```diff
-	"batch_size": 60,
+	"batch_size": 10,

-	"version": "GENERATED-TRAINING"
+	"version": "GENERATED-TRAINING-LOW-MEMORY"
```

## Training

```bash
cd ~/git/Multilingual_Text_to_Speech
conda activate ./env #only if env is not already active

export PYTHONIOENCODING=utf-8
python train.py --hyper_parameters generated_training_low_memory
```