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
from pydub.effects import normalize

MASTER_TEXT:str="entries.txt"
LONG_TEXT:str="entries-timestamps.txt"

if __name__ == "__main__":
    
    mp3Combined:str="mp3-combined"
    
    dname=os.path.dirname(sys.argv[0])
    if len(dname)>0:
        os.chdir(dname)
    
    print("Cleaning up from previous session")
    rmtree(mp3Combined, ignore_errors=True)
    pathlib.Path(".").joinpath(mp3Combined).mkdir(exist_ok=True)
    
    print("Loading list and calculating total audio length")
    
    haveLength:int=0
    entries: list = list()
    with open(MASTER_TEXT, "r") as f:
        for mp3 in f:
            entries.append(mp3.strip())
                        
    print(f"Have {len(entries):,} entries.")    
    
    totalTime:float=0
    totalCount:int=0
    
    already:list=set()
    
    with open(LONG_TEXT, "w") as f:
        f.write("")

    track:AudioSegment=AudioSegment.silent(500, 22050)
    
    print("Creating composite track")
    
    speechTime:int=0
    for entry in entries:
        entry=entry.strip()
        position:float=track.duration_seconds
        audioData:AudioSegment = AudioSegment.from_mp3(entry)
        speechTime+=audioData.duration_seconds
        track += normalize(audioData)
        track += AudioSegment.silent(500, 22050)
        with open(LONG_TEXT, "a") as f:
            f.write(f"{position:.2f}")
            f.write("|")
            f.write(f"{entry}")
            f.write("|")
            f.write("\n")
    
    totalTime=track.duration_seconds
    print("Exporting MP3")
    track.export(mp3Combined+"/composite.mp3")
    print("")
    print(f"Total speech time (minutes): {int(speechTime/60)}")
    print(f"Total track time (minutes): {int(totalTime/60)}")    
    print("Folder:",pathlib.Path(".").resolve().name)
    
    sys.exit(0)
    