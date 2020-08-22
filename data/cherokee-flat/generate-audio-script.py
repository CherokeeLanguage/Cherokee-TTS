#!/usr/bin/env python3
import os
import sys
import string
import unicodedata as ud
import random

os.chdir(os.path.dirname(sys.argv[0]))

v_notwanted = ["á", "é", "í", "ó", "ú", "v́", "a̋", "e̋",
               "i̋", "ő", "ű", "v̋", "à", "è", "ì", "ò",
               "ù", "v̀", "ǎ", "ě", "ǐ", "ǒ", "ǔ", "v̌",
               "â", "ê", "î", "ô", "û", "v̂"]

scripta:list = []
scriptb:list = []

with open("ced-multi.txt", "r") as f:
    entries: list = []
    for line in f:
        text: str=line.split("|")[1].strip().lower()
        if "," in text:
            tmp:list=text.split(",")
            for t in tmp:
                if t.strip() in entries:
                    continue
                entries.append(t.strip())
        else:
            if text in entries:
                continue
            entries.append(text)
            
for text in entries:
    text=ud.normalize('NFC', text)
    if "hgw" in text:
        continue
    if " " in text:
        continue
    if "b" in text:
        continue
    if "r" in text:
        continue
    if "hl" in text:
        continue
    if "tl" in text:
        continue
    if "hdl" in text:
        continue
    if "wh" in text:
        continue
    if "yh" in text:
        continue
    if "kws" in text:
        continue
    if "tsg" in text:
        continue
    if "nhd" in text:
        continue
    if "nhg" in text:
        continue
    if text[-2:-1] == "dl":
        continue
    for v in v_notwanted:
        v=ud.normalize('NFC', v)
        if v in text:
            break
    else:
        if text[-1] in "aeiouv":
            scripta.append(ud.normalize('NFC',text+"̄"))
            ytext = text
            while ytext[-1] in "aeiouv":
                ytext = ytext[:-1]
            if ytext[-1] in "hwyɂ":
                continue
            if len(ytext) == 1:
                continue
            if ytext[-2:] == "dl":
                continue
            if ytext[-2:] == "dt":
                continue
            if ytext[-2:] == "td":
                continue
            if ytext[-2:-1] == "h":
                continue
            if ytext[-2:-1] == "ɂ":
                continue
            scriptb.append(ytext)
        else:
            scripta.append(ud.normalize("NFC", text))

scripta += scriptb

for x in [1, 2, 3, 4]:

    random.Random(x).shuffle(scripta)
    line:str = ""
    cntr:int=1
    
    script:str = "# Script for low-tone only words.\n"
    script+="\n"
    script+="The macron on trailing vowels means keep the vowel at a low tone and to not use\n"
    script+="the normal high-fall.\n"
    script+="\n"
    script+="Please read each line like a sentence with appropriate pauses based on punctuation.\n"
    script+="\n"
    script+="If you can manage it (not required):\n"
    script+="\n"
    script+="* Final vowels should be nasalized.\n"
    script+="* Vowels preceeded by 'n' or 'm' should be nasalized.\n"
    script+="* Correct cadence between long and short vowels is the most important consideration.\n"
    script+="\n"
    script+="Each line needs to be recorded into a separate file with the filename indicating the\n"
    script+="script number as well as the line number.\n"
    script+="\n"
    script+="* Example for script 1, line 12: 1-12.mp3\n"
    script+="\n"
    script+="If you don't like your pronunciation for any line, skip it.\n"
    script+="\n"
    script+="Notes:\n"
    script+="\n"
    script+="* Enclosed SHORT vowels followed by an 'h', such as in the word 'tehgā' should be\n"
    script+="pronounced double-short with an equal length h sound following.\n"
    script+="\n"
    script+="* LONG vowels followed by an 'h', such as in the word 'gv:hnā', should have the 'h'\n"
    script+="pronounced as the start of the next syllable.\n"
    script+="\n\n"
    script+="## Script "+str(x)
    script+="\n\n"
    for text in scripta:
        if len(line) + len(text) > 30:
            script += str(cntr)+") "+line+".\n" 
            line=""
            cntr+=1
        else:
            if len(line)>0:
                line+=", "
            line+=text
    if len(line)>0:
        script += str(cntr)+") "+line+".\n"
        
    with open("script-"+str(x)+".txt", "w") as w:
        w.write(script)

sys.exit()
