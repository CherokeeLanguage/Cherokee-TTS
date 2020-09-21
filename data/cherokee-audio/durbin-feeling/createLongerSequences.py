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
    
    minLength:int=60*40
    
    dname=os.path.dirname(sys.argv[0])
    if len(dname)>0:
        os.chdir(dname)

    
    MASTER_TEXT:str="aeneas.txt"
    LONG_TEXT:str="durbin-feeling-longer-sequences.txt"
    
    print("Cleaning up from previous session")

    rmtree("mp3-long", ignore_errors=True)
    pathlib.Path(".").joinpath("mp3-long").mkdir(exist_ok=True)
    
    print("Loading list and calculating total audio length")
    
    haveLength:int=0
    with open(MASTER_TEXT, "r") as f:
        entriesDict: dict = {}
        for line in f:
            spkr: str=line.split("|")[0].strip()
            mp3: str=line.split("|")[1].strip()
            text: str=ud.normalize("NFD", line.split("|")[2].strip())
            if text=="":
                continue
            entriesDict[text]=(mp3,text, spkr)
            haveLength += AudioSegment.from_mp3(mp3).duration_seconds
    
    tmpEntries:list=[e for e in entriesDict.values()]
    speakers:set=set([e[2] for e in tmpEntries])
    if len(speakers)>1:
        print("Speakers:",speakers)
        
    print(f"Have {len(tmpEntries):,} starting entries with {len(speakers):,} speakers.")    
    print(f"Available audio duration (minutes): {int(haveLength/60)}")
    
    entries:list=[]
    _:int=0
    minLength=min(minLength, haveLength*3)
    workingLength:int=0
    while workingLength < minLength:
        _+=1
        random.Random(_).shuffle(tmpEntries)
        entries.extend(tmpEntries)
        workingLength+=haveLength
    
    print(f"Have {len(entries):,} entries with {len(speakers):,} speakers.")
    print(f"Target duration (minutes): {int(workingLength/60)}")
    
    dice=random.Random(len(entries))
    
    with open(LONG_TEXT, "w") as f:
        f.write("")
        
    totalTime:float=0
    totalCount:int=0
    
    already:list=[]
    text:str=""
    track:AudioSegment=AudioSegment.empty()
    wantedLen=dice.randint(0, 6)+dice.randint(0, 6)+dice.randint(0, 6)
    for ix, entry in enumerate(entries):
        audioData:AudioSegment = AudioSegment.from_mp3(entry[0].replace("mp3/", "mp3-b/"))
        audioText:str = entry[1].strip()
        spkr:str=entry[2]
        if ix % 100 == 0:
            print(f"... {audioText} [ix={ix:,}, {int(ix/len(entries)*100):d}%]")
        if len(audioText)==0:
            continue
        if audioText[-1] not in ".,?!":
            audioText+="."
        if audioData.duration_seconds + track.duration_seconds > wantedLen and track.duration_seconds>0:
            if text not in already:
                totalTime+=track.duration_seconds
                totalCount+=1
                track.export(f"mp3-long/{ix:06d}.mp3", format="mp3", bitrate="192")
                already.append(text)
                with open(LONG_TEXT, "a") as f:
                    f.write(f"{spkr}")
                    f.write("|")
                    f.write(f"mp3-long/{ix:06d}.mp3")
                    f.write("|")
                    f.write(ud.normalize("NFC", text))
                    f.write("\n")
            text=""
            track=AudioSegment.empty()
            wantedLen=dice.randint(1, 4)+dice.randint(1, 4)+dice.randint(1, 4)
        
        if len(track) > 0:
            track += AudioSegment.silent(500, 22050)
        track += match_target_amplitude(audioData, -16)
        
        if len(text)>0:
            text += " "
        text += audioText
        
    if len(track)>0 and text not in already:
        totalTime+=track.duration_seconds
        totalCount+=1
        track.export(f"mp3-long/{ix+1:06d}.mp3", format="mp3", bitrate="192")
        with open(LONG_TEXT, "a") as f:
                    f.write(f"{spkr}")
                    f.write("|")
                    f.write(f"mp3-long/{ix+1:06d}.mp3")
                    f.write("|")
                    f.write(ud.normalize("NFC", text))
                    f.write("\n")
                
    print(f"Average track time: {totalTime/totalCount:.2f}. Total tracks: {totalCount:,}")
    
    print("Folder:",pathlib.Path(".").resolve().name)
    
    sys.exit()
    