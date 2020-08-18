import os
import subprocess
import re

HOME = os.path.expanduser("~")
WORK = HOME + "/git/Multilingual_Text_to_Speech/data/cherokee"
SRC = WORK + "/common-voice-clean.txt"
DEST = WORK + "/mogrified-common-voice-clean.txt"

espeak=HOME+"/espeak-ng/bin/espeak-ng"

metadata = []

with open(SRC, 'r', encoding="utf-8") as f:
    metadata.append(([line.rstrip().split('|') for line in f]))
    
with open(DEST, "w", encoding="utf-8") as f:
    for meta in metadata:
        for m in meta:
            idx, spkr, lang, wav, text = m
            
            result = subprocess.run([espeak, "--ipa", "-q", "-v", lang, text], stdout=subprocess.PIPE)
            ytext=result.stdout.decode("utf-8").strip()
            
            if ("?" in ytext):
                continue
            if ("(" in ytext):
                continue
            if ("|" in ytext):
                continue
            
            ytext = ytext.replace("\n", ", ")
            if (text[-1] in ".?!:;"):
                ytext = ytext + text[-1]
            else:
                ytext = ytext + "."
            ytext = re.sub("(?im)\\s+", " ", ytext)
            
            xtext = ytext
            
            xtext = re.sub("v", "@", xtext)
            xtext = re.sub("a", "@", xtext)
            xtext = re.sub(":", "@", xtext)
            
            #skip any entries with core orthography conflicts
            if ("@" in xtext):
                continue
            
            xtext = re.sub("ɑ", "a", xtext)
            xtext = re.sub("ə̃", "v", xtext)
            xtext = re.sub("œ̃", "v", xtext)
            
            xtext = re.sub("ə", "v", xtext)
            xtext = re.sub("œ", "v", xtext)
            
            xtext = re.sub("ː", ":", xtext)
            xtext = re.sub("dʒ", "j", xtext)
            xtext = re.sub("tʃ", "ch", xtext)
            
            xtext = re.sub("tɬ", "tl", xtext)
            xtext = re.sub("ɬ", "hl", xtext)
            xtext = re.sub("ʔ", "ɂ", xtext)
            
            if (not "v" in xtext):
                continue
            
            print(f'{idx}|{spkr}|{lang}|{wav}|{xtext}', file=f)
    