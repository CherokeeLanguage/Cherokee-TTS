#!/usr/bin/env python3
import os
import sys
import string
import unicodedata as ud
import random
import re
import pathlib
import subprocess
from shutil import rmtree

from md2pdf.core import md2pdf
from cairosvg.shapes import line

os.chdir(os.path.dirname(sys.argv[0]))

MASTER_TEXT:str="sam-hider.txt"

#cleanup any previous runs
for dir in ["linear_spectrograms", "spectrograms", "wav"]:
    rmtree(dir, ignore_errors=True)
    
pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)

with open(MASTER_TEXT, "r") as f:
    entries: dict = {}
    for line in f:
        mp3: str=line.split("|")[0].strip()
        text: str=ud.normalize("NFD", line.split("|")[1].strip())
        if text=="":
            continue
        entries[text]=(mp3,text)

voiceid:str=""
with open("voice-id.txt", "r") as f:
    for line in f:
        voiceid=line.strip()
        break

id:int=10000 * int(re.sub("^(\d+).*", "\\1",voiceid))

rows:list=[]
for mp3, text in entries.values():
    wav:str="wav/"+os.path.splitext(os.path.basename(mp3))[0]+".wav"
    text:str=ud.normalize('NFC', text)
    subprocess.run(["ffmpeg","-i",mp3,"-ac","1","-ar","22050",wav], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    rows.append(f"{id:06d}|{voiceid}|chr|{wav}|||{text}|")
    id+=1

#save all copy before shuffling
with open("all.txt", "w") as f:
    for line in rows:
        f.write(line)
        f.write("\n")

#create train/val sets                        
random.Random(id).shuffle(rows)
trainSize:int=(int)(len(rows)*.95)
with open("train.txt", "w") as f:
    for line in rows[:trainSize]:
        f.write(line)
        f.write("\n")
        
with open("val.txt", "w") as f:
    for line in rows[trainSize:]:
        f.write(line)
        f.write("\n")
        

sys.exit()
