#!/usr/bin/env python3
import os
import sys
import unicodedata as ud
import random
import pathlib
from shutil import rmtree

from pydub import AudioSegment
import pydub.effects as effects
from split_audio import detect_sound
from builtins import list

if __name__ == "__main__":

    os.chdir(os.path.dirname(sys.argv[0]))
    
    MASTER_TEXT:str="comvoi-clean.txt"
    max_duration:float=10.0
    
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
    
    shortestLength:float=-1
    longestLength:float=0.0
    totalLength:float=0.0
    print("Creating wavs")
    rows:list=[]
    for xid, speaker, lang, mp3, text in entries.values():
        wav:str="wav/"+os.path.splitext(os.path.basename(mp3))[0]+".wav"
        text:str=ud.normalize('NFD', text)
        mp3_segment:AudioSegment=AudioSegment.from_file(mp3)
        segments:list = detect_sound(mp3_segment)
        if len(segments) > 1:
            mp3_segment=mp3_segment[segments[0][0]:segments[-1][1]]
        if mp3_segment.duration_seconds > max_duration:
            continue
        audio:AudioSegment = AudioSegment.silent(125, 22050)
        audio = audio.append(mp3_segment, crossfade=0)
        audio = audio.append(AudioSegment.silent(125, 22050))
        audio = effects.normalize(audio)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(22050)
        audio.export(wav, format="wav")
        totalLength+=audio.duration_seconds
        if shortestLength < 0 or shortestLength > audio.duration_seconds:
            shortestLength = audio.duration_seconds
        if longestLength < audio.duration_seconds:
            longestLength = audio.duration_seconds
        rows.append(f"{xid}|{speaker}|{lang}|{wav}|||{text}|")
    
    totalLength=int(totalLength)
    minutes=int(totalLength/60)
    seconds=int(totalLength%60)
    print(f"Total duration: {minutes:,}:{seconds:02}")
    
    shortestLength=int(shortestLength)
    minutes=int(shortestLength/60)
    seconds=int(shortestLength%60)
    print(f"Shortest duration: {minutes:,}:{seconds:02}")
    
    longestLength=int(longestLength)
    minutes=int(longestLength/60)
    seconds=int(longestLength%60)
    print(f"Longest duration: {minutes:,}:{seconds:02}")
    
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
