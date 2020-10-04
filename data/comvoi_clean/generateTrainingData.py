#!/usr/bin/env python3
import os
import sys
import unicodedata as ud
import random
import pathlib
import subprocess
from shutil import rmtree

if __name__ == "__main__":

    os.chdir(os.path.dirname(sys.argv[0]))
    
    MASTER_TEXT:str="comvoi-clean.txt"
    
    rmtree("wav", ignore_errors=True)
    pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)
    langs:set=set()
    
    with open(MASTER_TEXT, "r") as f:
        entries: dict = {}
        for line in f:
            fields=line.split("|")
            xid: str=fields[0].strip()
            spkr: str=fields[1].strip()
            lang: str=fields[2].strip()        
            mp3: str=fields[3].strip()        
            text: str=ud.normalize("NFD", fields[6].strip())
            dedupeKey=spkr+"|"+text
            if text=="":
                continue
            entries[dedupeKey]=(xid,spkr,lang,mp3,text)
            langs.add(lang)
    
    print(f"Loaded {len(entries):,} entries with audio and text.")
    
    print("Creating wavs")
    rows:list=[]
    for xid, speaker, lang, mp3, text in entries.values():
        wav:str="wav/"+os.path.splitext(os.path.basename(mp3))[0]+".wav"
        text:str=ud.normalize('NFC', text)
        subprocess.run(["ffmpeg","-y","-i",mp3,"-ac","1","-ar","22050",wav], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rows.append(f"{xid}|{speaker}|{lang}|{wav}|||{text}|")
    
    print("Creating training files")
    
    #save all copy before shuffling
    with open("all.txt", "w") as f:
        for line in rows:
            f.write(line)
            f.write("\n")
            
    with open("train.txt", "w") as f:
        f.write("")
    with open("val.txt", "w") as f:
        f.write("")
        
            
    for lang in langs:
        subset:list=list()
        for row in rows:
            rlang = row.split("|")[2]
            if rlang != lang:
                continue
            subset.append(row)
        print(f" {lang} length: {len(subset):,}")
        random.Random(len(subset)).shuffle(subset)
        #create train/val sets - splitting up data by language evenly
        trainSize:int=(int)(len(subset)*.95)
        valSize:int=len(subset)-trainSize
        with open("train.txt", "a") as f:
            for line in subset[:trainSize]:
                f.write(line)
                f.write("\n")
                
        with open("val.txt", "a") as f:
            for line in subset[trainSize:]:
                f.write(line)
                f.write("\n")
        print(f"  Train size for {lang}: {trainSize}")
        print(f"   Val size for {lang}: {valSize}")
    
    print(f"All size: {len(rows)}")
    print("Folder:",pathlib.Path(".").resolve().name)        
    
    sys.exit()
