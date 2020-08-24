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

os.chdir(os.path.dirname(sys.argv[0]))

rmtree("wav", ignore_errors=True)
pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)

with open("sam-hider.txt", "r") as f:
    entries: list = []
    for line in f:
        mp3: str=line.split("|")[0].strip()
        text: str=ud.normalize("NFD", line.split("|")[1].strip())
        entries.append((mp3,text))

voiceid:str=""
with open("voice-id.txt", "r") as f:
    for line in f:
        voiceid=line.strip()
        break

id:int=120000

FNULL = open(os.devnull, 'w')
rows:list=[]
for mp3, text in entries:
    wav:str="wav/"+os.path.splitext(os.path.basename(mp3))[0]+".wav"
    text:str=ud.normalize('NFC', text)
    subprocess.run(["ffmpeg","-i",mp3,"-ac","1","-ar","22050",wav], check=True, stdout=FNULL, stderr=FNULL)
    # 100201|01-chr|chr|../cherokee/ma-split/Track_45-006.wav|../cherokee/spectrograms/100201.npy|../cherokee/linear_spectrograms/100201.npy|sǔ:dáli.|
    rows.append(f"{id:06d}|{voiceid}|chr|../../cherokee-audio/sam-hider/{wav}|||{text}|")
    id+=1

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
