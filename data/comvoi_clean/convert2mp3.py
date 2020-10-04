#!/usr/bin/env python3

import os
import sys
import unicodedata as ud
import pathlib
from pydub import AudioSegment
import pydub.effects as effects
from shutil import rmtree

META:str="meta.csv"
ALL_LANG:set=set(("de", "fr", "nl", "ru", "zh"))
DEST:str="mp3"
ALL:str="comvoi-clean.txt"

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms
    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0  # ms
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
        trim_ms += chunk_size

    return trim_ms

if __name__ == "__main__":
    
    entries:set=set()
    
    dname=os.path.dirname(sys.argv[0])
    if len(dname)>0:
        os.chdir(dname)
        
    print("Cleaning up from previous session")
    rmtree(DEST, ignore_errors=True)
    pathlib.Path(".").joinpath(DEST).mkdir(exist_ok=True)
    
    idx:int=0
    
    for lang in ALL_LANG:
        skipped:int=0
        print(f"Processing {lang}")
        with open(lang+"/"+META) as f:
            entriesDict: dict = {}
            for line in f:
                spkr: str=line.split("|")[0].strip()
                wav: str=str(pathlib.Path(".").joinpath(lang, "wavs", spkr, line.split("|")[1].strip()))
                text: str=ud.normalize("NFD", line.split("|")[2].strip())
                if text=="":
                    continue
                if not os.path.exists(wav):
                    continue
                entriesDict[text]=(wav,text,spkr)
            
            for entry in entriesDict.values():
                idx+=1
                wav=entry[0]
                text:str=ud.normalize("NFC", entry[1])
                spkr:str=entry[2]+"-"+lang
                mp3:str=str(pathlib.Path(DEST).joinpath(f"{lang}-{spkr}-{idx:06}.mp3"))
                
                audio=AudioSegment.from_file(wav)
                prelength=audio.duration_seconds
                audio=effects.normalize(audio)
                
                start_trim = detect_leading_silence(audio, silence_threshold=-40, chunk_size=150)
                end_trim = detect_leading_silence(audio.reverse(), silence_threshold=-40, chunk_size=150)
                duration = len(audio)
                start_trim=max(0, start_trim-50)
                end_trim=min(0, end_trim-50)
                audio = audio[start_trim:duration-end_trim]
                
                postlength=audio.duration_seconds
                if prelength!=postlength:
                    if postlength/prelength<0.95:
                        skipped+=1
                        #print(f"\tTrimmed {wav} {mp3} from {prelength,} to {postlength,}")
                        continue
                    
                audio.export(mp3, format="mp3", bitrate="192")
                entries.add((idx, spkr, lang, mp3, text))
            
            print(f"   Skipped {skipped:,} potentially bad entries")
            
    print(f"Creating final {ALL}")
    with open(ALL, "w") as f:
        for entry in entries:
            idx=entry[0]
            spkr=entry[1]
            lang=entry[2]
            mp3=entry[3]
            text=entry[4]
            f.write(f"{idx:06}|{spkr}|{lang}|{mp3}|||{text}|\n")
    
    print("Done")
    os.sys.exit()
    
    
                