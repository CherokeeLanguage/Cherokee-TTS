#!/usr/bin/env python3

if __name__ == "__main__":
    import os
    import sys
    import csv
    import codecs
    import re
    import json
    
    from chrutils import ascii_ced2mco
    from chrutils import ascii_ced2ced
    
    dname=os.path.dirname(sys.argv[0])
    if len(dname)>0:
        os.chdir(dname)
        
    matches:dict=dict()
    with open("matches.txt", "r") as file:
        for line in file:
            fields=line.split("|")
            mco=fields[2].strip()
            mp3=fields[3].strip()
            matches[mp3]=mco
            
    cno_web:dict=dict()
    with open("cno-web.txt", "r") as file:
        for line in file:
            fields=line.split("|")
            mco=fields[0].strip()
            mp3=fields[1].strip()
            cno_web[mp3]=mco
            
    cno_web_syl:dict=dict()
    with open("cno-web-syl.txt", "r") as file:
        for line in file:
            fields=line.split("|")
            mco=fields[0].strip()
            mp3=fields[1].strip()
            cno_web_syl[mp3]=mco
            
    speakers:dict=dict()
    with open("mp3-speaker-lookup.txt", "r") as file:
        for line in file:
            fields=line.split("|")
            speaker=fields[1]
            mp3=fields[2]
            speakers[mp3]=speaker
    
    speaker_counts:dict=dict()
    with open("cno-training-data.txt", "w") as file:
        for mp3 in [*matches]:
            speaker=speakers[mp3]
            mco=matches[mp3]
            print(f"{speaker}|cno_cwl/{mp3}|{mco}", file=file)
            if speaker not in speaker_counts:
                speaker_counts[speaker]=1
            else:
                speaker_counts[speaker]=speaker_counts[speaker]+1
        for mp3 in [*cno_web]:
            speaker=speakers[mp3]
            mco=cno_web[mp3]
            print(f"{speaker}|cno_cwl/{mp3}|{mco}", file=file)
            if speaker not in speaker_counts:
                speaker_counts[speaker]=1
            else:
                speaker_counts[speaker]=speaker_counts[speaker]+1
        for mp3 in [*cno_web_syl]:
            speaker=speakers[mp3]
            syl=cno_web_syl[mp3]
            print(f"{speaker}|cno_cwl/{mp3}|{syl}", file=file)
            if speaker not in speaker_counts:
                speaker_counts[speaker]=1
            else:
                speaker_counts[speaker]=speaker_counts[speaker]+1
    
    count=len(matches)
    print(f"Entries: {count:,}")
    print()
    print("Speaker Counts:")
    speakers=[*speaker_counts]
    speakers.sort()
    for speaker in speakers:
        count=speaker_counts[speaker]
        print(f"   {speaker}: {count:,}")
        