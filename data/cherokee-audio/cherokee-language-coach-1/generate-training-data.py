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

MASTER_TEXT:str="coach-1-selected.txt"

#cleanup any previous runs
for dir in ["linear_spectrograms", "spectrograms", "wav"]:
    rmtree(dir, ignore_errors=True)
    
pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)

with open(MASTER_TEXT, "r") as f:
    entries: dict = {}
    for line in f:
        fields=line.split("|")
        speaker: str=fields[0].strip()
        mp3: str=fields[1].strip()
        text: str=ud.normalize("NFD", fields[2].strip())
        dedupeKey=speaker+"|"+text
        if text=="":
            continue
        entries[dedupeKey]=(speaker,mp3,text)

print(f"Loaded {len(entries):,} entries with audio and text.")

#the voice id to use for any "?" marked entries
voiceid:str=""
with open("voice-id.txt", "r") as f:
    for line in f:
        voiceid=line.strip()
        break
    
#to map any non "?" marked entries from annotation short hand id to ML assigned sequence id
voiceids:dict = {}
with open("../voice-ids.txt") as f:
    for line in f:
        mapping=line.strip()
        fields = mapping.split("|")
        if len(fields)<2 or fields[1].strip() == "":
            break
        id=fields[0].strip()
        if id.strip()=="":
            continue
        for field in fields[1:]:
            if field.strip() == "":
                continue
            voiceids[field.strip()]=id

id:int=10000 * int(re.sub("^(\d+).*", "\\1",voiceid))

print("Creating wavs")
rows:list=[]
for speaker, mp3, text in entries.values():
    wav:str="wav/"+os.path.splitext(os.path.basename(mp3))[0]+".wav"
    text:str=ud.normalize('NFC', text)
    subprocess.run(["ffmpeg","-i",mp3,"-ac","1","-ar","22050",wav], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    vid:str=speaker
    if vid in voiceids.keys():
        vid = voiceids[vid]
    if vid=="?":
        vid=voiceid
    
    rows.append(f"{id:06d}|{vid}|chr|{wav}|||{text}|")
    id+=1

print("Creating training files")
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
