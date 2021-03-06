#!/usr/bin/env python3
import os
import sys
import string
import unicodedata as ud
import random
import re
import csv

from chrutils.chrutils import ced2mco
from chrutils.chrutils import ascii_ced2mco

os.chdir(os.path.dirname(sys.argv[0]))

CED:str="ced_202008231250.csv"

ASCII_CED_TONES=["nounadjpluraltone", "vfirstprestone", "vsecondimpertone", "vthirdinftone", "vthirdpasttone", "vthirdprestone"]

trans2ced = {}

CGRAVEACCENT="\u0300"
CACUTEACCENT="\u0301"
CCARON="\u0302"
CMACRON="\u0304"
CDOUBLEACUTE="\u030b"
CCIRCUMFLEX="\u030c"
CMACRONBELOW="\u0331"

#Build guessing pronunciation lookup for transliterated text
with open(CED, newline='') as csvfile:
    rows = csv.DictReader(csvfile)
    for row in rows:
        for key in ASCII_CED_TONES:
            value:str = row[key]
            if (value == ""):
                continue
            value=ud.normalize("NFD", ascii_ced2mco(value)).lower()
            cedKey:str=re.sub("(?i)[^a-z.,;?! ]", "", value).lower()
            if cedKey=="":
                continue
            
            trans2ced[cedKey]=value
            trans2ced[cedKey.capitalize()]=value.capitalize()
            
            #some common clitics
            trans2ced[cedKey+"s"]=value+"s"
            trans2ced[cedKey.capitalize()+"s"]=value.capitalize()+"s"
            
            if cedKey[-1] in "aeiouv":
                cedKey2=cedKey[:-1]
                value2=value[:-1]
                if value2[-1] == "ɂ":
                    value2=value2[:-1]
                if value2[-1] == ":":
                    value2=value2[:-1]
                if value2[-1] == CCARON:
                    value2 = value2[:-1] + CACUTEACCENT
                if value2[-1] == CCIRCUMFLEX:
                    value2 = value2[:-1] + CACUTEACCENT
                if value2[-1] == CGRAVEACCENT:
                    value2 = value2[:-1]+CMACRON
                #some common clitics
                trans2ced[cedKey+"s"]=value+"s"
                trans2ced[cedKey.capitalize()+"s"]=value.capitalize()+"s"
                
with open(CED, newline='') as csvfile:
    rows = csv.DictReader(csvfile)
    for row in rows:
        sentence:str = row["sentenceq"]
        
        if sentence.strip() == "":
            continue
        
        sentence = sentence.replace(".", " .")
        sentence = sentence.replace(",", " ,")
        sentence = sentence.replace("?", " ?")
        sentence = sentence.replace("!", " !")
        
        sentence = " " + sentence + " "
        
        sentence = re.sub("<.*?>", "", sentence)
        
        newSentence = sentence
        found:bool = False
        for word in sentence.split(" "):
            if word.strip()=="":
                continue
            if word in ".,!?:;0123456789()\"'$%:":
                continue
            if word not in trans2ced:
                badWord = re.sub("(.)", "\\1"+CMACRONBELOW, word)
                newSentence=newSentence.replace(word+" ", badWord+" ")
            else:
                found = True
                newSentence=newSentence.replace(word+" ", trans2ced[word]+" ")
                #if k+" " in newSentence:
                #    newSentence = newSentence.replace(k+" ", v+" ")
        if (found):
            print(newSentence)

sys.exit()

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
        if re.match(".*?[aeiouv]h.*", text):
            continue
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
    
    random.Random(x).shuffle(scripta) #fixed shuffle based on script no, for reproducibility
    randx = random.Random(x) #fixed random number set based on script no, for reproducibility
    
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
    wordCntr:int=0
    wordCommand:int=0
    for text in scripta:
        if wordCntr==0:
            #basic bell curve, range: 1 to 11, for word count per "sentence".
            lineLength:int=0
            for _ in range(10):
                lineLength += randx.randint(0, 1) + 1
            lineLength -= 9
            wordComma=randx.randint(2,10) #random clause marks
        if wordCntr >= lineLength:
            script += str(cntr)+". "+line+".\n" 
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
        script += str(cntr)+". "+line+".\n"
        
    with open("script-"+str(x)+".txt", "w") as w:
        w.write(script)
    with open("script-"+str(x)+".md", "w") as w:
        w.write(script)

sys.exit()
