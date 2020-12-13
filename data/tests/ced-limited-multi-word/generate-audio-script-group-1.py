#!/usr/bin/env python3
import os
import sys
import string
import unicodedata as ud
import random
import re

from md2pdf.core import md2pdf

os.chdir(os.path.dirname(sys.argv[0]))

clist=" abcdefghijklmnopqrstuvwxyzçèéßäöōǎǐíǒàáǔüèéìūòóùúāēěīâêôûñőűабвгдежзийклмнопрстуфхцчшщъыьэюяёɂāēīōūv̄àèìòùv̀ǎěǐǒǔv̌âêîôûv̂áéíóúv́a̋e̋i̋őűv̋¹²³⁴ạẹịọụṿ"
#print("CLIST")
#print(ud.normalize('NFC',clist))
xlist = ""
for c in clist:
    if c not in xlist:
        xlist += c
#print("XLIST")
#print(ud.normalize('NFC',xlist))

v_notwanted = ["á", "é", "í", "ó", "ú", "v́", "a̋", "e̋",
               "i̋", "ő", "ű", "v̋", "à", "è", "ì", "ò",
               "ù", "v̀", "ǎ", "ě", "ǐ", "ǒ", "ǔ", "v̌",
               "â", "ê", "î", "ô", "û", "v̂"]

scripta:list = []
scriptb:list = []

with open("ced-mco.txt", "r") as f:
    entries: list = []
    for line in f:
        fields:list=line.split("|")
        for field in fields[1:8]:
            text: str=field.strip().lower()
            if text == "":
                continue
            if "-" in text:
                continue
            if " " in text:
                continue
            if text[-1] in ".,!?":
                text=text[:-1]
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
    if re.match("(?i).*[yw][cdghjklmnst].*", text):
        continue
    if re.match("(?i).*[cdghjklmnst]{3,}.*", text):
        continue
    if text[-2:-1] == "dl":
        continue
    for v in v_notwanted:
        v=ud.normalize('NFC', v)
        if v in text:
            break
    else:
        if re.match(".*?[aeiouv]h.*", text):
            continue
        if text[-1] in "aeiouv":
            scripta.append(ud.normalize('NFC',text)) #+"̄"))
            ytext = text
            while ytext[-1] in "aeiouvɂ":
                ytext = ytext[:-1]
            while ytext[-1] == ":":
                ytext = ytext[:-1]
            if ytext[-1] in "hwyɂ":
                continue
            if len(ytext) < 2:
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

for x in [1]:
    
    random.Random(x).shuffle(scripta) #fixed shuffle based on script no, for reproducibility
    randx = random.Random(x) #fixed random number set based on script no, for reproducibility
    
    line:str = ""
    cntr:int=1
    
    synscript:str = ""
    
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
    wordCntr:int=0
    wordCommand:int=0
    for text in scripta:
        if wordCntr==0:
            #basic bell curve, range: 1 to 4, for word count per "sentence".
            lineLength:int=0
            for _ in range(1):
                lineLength += randx.randint(0, 1) + 1
            lineLength -= 0
            wordComma=randx.randint(2,10) #random clause marks
        if wordCntr >= lineLength:
            script += str(cntr)+". "+line.strip()+".\n"
            synscript += line.strip()+".|(Random dictionary entries.)\n"
            line=""
            lineLength=0
            wordCntr=0
            cntr+=1
        else:
            wordCntr += 1
            if len(line)==0:
                text=text.capitalize()
            if len(line)>0 and wordCntr==wordComma:
                if randx.randint(0,1)==0:
                    line+=", "
                else:
                    line+=". "
                    text=text.capitalize()
            else:
                line+=" "
            line+=text
    if len(line)>0:
        script += str(cntr)+". "+line.strip()+".\n"
        synscript += line.strip()+".|(Random dictionary entries.)\n"
    
    with open("scripts/script-bare-"+str(x)+".txt", "w") as w:
        w.write(synscript)
    with open("scripts/script-"+str(x)+".txt", "w") as w:
        w.write(script)
    with open("scripts/script-"+str(x)+".md", "w") as w:
        w.write(script)
    md2pdf("scripts/script-"+str(x)+".pdf", script.replace("## Script", "<div style=\"page-break-after: always\"></div>\n\n## Script"))
sys.exit()
