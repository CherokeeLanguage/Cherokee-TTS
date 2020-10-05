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
from pydub import AudioSegment
import pydub.effects as effects

if __name__ == "__main__":

    if (sys.argv[0].strip()!=""):
        os.chdir(os.path.dirname(sys.argv[0]))
    
    MASTER_TEXTS:list=["aeneas.txt"]
    
    #cleanup any previous runs
    for dir in ["linear_spectrograms", "spectrograms", "wav"]:
        rmtree(dir, ignore_errors=True)
        
    pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)
    
    entries: dict = {}
    for MASTER_TEXT in MASTER_TEXTS:
        with open(MASTER_TEXT, "r") as f:
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
    
    id:int=1
    
    totalLength:float=0.0
    print("Creating wavs")
    rows:list=[]
    for speaker, mp3, text in entries.values():
        wav:str="wav/"+os.path.splitext(os.path.basename(mp3))[0]+".wav"
        text:str=ud.normalize('NFC', text)
        audio=AudioSegment.from_file(mp3)
        audio = effects.normalize(audio)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(22050)
        audio.export(wav, format="wav")
        totalLength+=audio.duration_seconds
        vid:str=speaker
        if vid in voiceids.keys():
            vid = voiceids[vid]
        if vid=="?":
            vid=voiceid        
        rows.append(f"{id:06d}|{vid}|chr|{wav}|||{text}|")
        id+=1
    
    totalLength=int(totalLength)
    minutes=int(totalLength/60)
    seconds=int(totalLength%60)
    print(f"Total duration: {minutes:,}:{seconds:02}")
    
    print("Creating training files")
    #save all copy before shuffling
    with open("all.txt", "w") as f:
        for line in rows:
            f.write(line)
            f.write("\n")
    
    #create train/val sets                        
    random.Random(id).shuffle(rows)
    trainSize:int=(int)(len(rows)*.95)
    valSize:int=len(rows)-trainSize
    
    with open("train.txt", "w") as f:
        for line in rows[:trainSize]:
            f.write(line)
            f.write("\n")
            
    with open("val.txt", "w") as f:
        for line in rows[trainSize:]:
            f.write(line)
            f.write("\n")
    
    print(f"Train size: {trainSize}")
    print(f"Val size: {valSize}")
    print(f"All size: {len(rows)}")
    print("Folder:",pathlib.Path(".").resolve().name)        
    
    sys.exit()
