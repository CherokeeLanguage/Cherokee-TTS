#!/usr/bin/env python3
import os
import sys
import string
import unicodedata as ud
import random
import re
import pathlib
import subprocess
from pydub import AudioSegment
from shutil import rmtree

# Define a function to normalize a chunk to a target amplitude.
def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)

if __name__ == "__main__":
    dname=os.path.dirname(sys.argv[0])
    if len(dname)>0:
        os.chdir(dname)

    
    MASTER_TEXT:str="sam-hider.txt"
    LONG_TEXT:str="sam-hider-longer-sequences.txt"

    rmtree("mp3-long", ignore_errors=True)
    pathlib.Path(".").joinpath("mp3-long").mkdir(exist_ok=True)
    
    with open(MASTER_TEXT, "r") as f:
        entriesDict: dict = {}
        for line in f:
            mp3: str=line.split("|")[0].strip()
            text: str=ud.normalize("NFD", line.split("|")[1].strip())
            if text=="":
                continue
            entriesDict[text]=(mp3,text)
    
    tmpEntries:list=[e for e in entriesDict.values()]
    
    entries:list=[]
    _:int=0
    while len(entries) < 5000:
        _+=1
        random.Random(_).shuffle(tmpEntries)
        entries.extend(tmpEntries)
    
    print(f"Have {len(entries):,} entries.")
    
    dice=random.Random(len(entries))
    
    with open(LONG_TEXT, "w") as f:
        f.write("")
        
    totalTime:float=0
    totalCount:int=0
    
    text:str=""
    track:AudioSegment=AudioSegment.empty()
    wantedLen=dice.randint(0, 6)+dice.randint(0, 6)+dice.randint(0, 6)
    for ix, entry in enumerate(entries):
        audioData:AudioSegment = AudioSegment.from_mp3(entry[0].replace("mp3/", "mp3-b/"))
        audioText:str = entry[1].strip()
        if ix % 100 == 0:
            print(f"... {audioText} [ix={ix:,}, {int(ix/len(entries)*100):d}%]")
        if len(audioText)==0:
            continue
        if audioText[-1] not in ".,?!":
            audioText+="."
        if audioData.duration_seconds + track.duration_seconds > wantedLen and track.duration_seconds>0:
            totalTime+=track.duration_seconds
            totalCount+=1
            track.export(f"mp3-long/{ix:06d}.mp3", format="mp3", bitrate="192")
            track=AudioSegment.empty()
            wantedLen=dice.randint(1, 4)+dice.randint(1, 4)+dice.randint(1, 4)
            with open(LONG_TEXT, "a") as f:
                f.write(f"mp3-long/{ix:06d}.mp3")
                f.write("|")
                f.write(ud.normalize("NFC", text))
                f.write("\n")
                text=""
        
        if len(track) > 0:
            track += AudioSegment.silent(500, 22050)
        track += match_target_amplitude(audioData, -16)
        
        if len(text)>0:
            text += " "
        text += audioText
        
    if len(track)>0:
        totalTime+=track.duration_seconds
        totalCount+=1
        track.export(f"mp3-long/{ix+1:06d}.mp3", format="mp3", bitrate="192")
        with open(LONG_TEXT, "a") as f:
                f.write(f"mp3-long/{ix+1:06d}.mp3")
                f.write("|")
                f.write(ud.normalize("NFC", text))
                f.write("\n")
                
    print(f"Total tracks: {totalCount:,}, Average track time: {totalTime/totalCount:.2f}")
    
    sys.exit()
    