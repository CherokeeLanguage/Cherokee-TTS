#!/usr/bin/env python3
import os
import sys
import string
import unicodedata as ud

os.chdir(os.path.dirname(sys.argv[0]))

v_notwanted = ["á", "é", "í", "ó", "ú", "v́", "a̋", "e̋",
               "i̋", "ő", "ű", "v̋", "à", "è", "ì", "ò",
               "ù", "v̀", "ǎ", "ě", "ǐ", "ǒ", "ǔ", "v̌",
               "â", "ê", "î", "ô", "û", "v̂"]

script = []

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
    if text[-2:-1] == "dl":
        continue
    for v in v_notwanted:
        v=ud.normalize('NFC', v)
        if v in text:
            break
    else:
        if text[-1] in "aeiouv":
            script.append(ud.normalize('NFC',text+"̄"))
            ytext = text
            while ytext[-1] in "aeiouv":
                ytext = ytext[:-1]
            if ytext[-1] in "hwyɂ":
                continue
            if len(ytext) == 1:
                continue
            if ytext[-2:] == "dl":
                continue
            if ytext[-2:-1] == "h":
                continue
            if ytext[-2:-1] == "ɂ":
                continue
            script.append(ytext)
        else:
            script.append(ud.normalize("NFC", text))

for text in script:
    print(text)
sys.exit()
