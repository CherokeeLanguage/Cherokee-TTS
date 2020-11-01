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
            
    speakers:dict=dict()
    with open("mp3-speaker-lookup.txt", "r") as file:
        for line in file:
            fields=line.split("|")
            speaker=fields[1]
            mp3=fields[2]
            speakers[mp3]=speaker
    
    with open("cno-training-data.txt", "w") as file:
        for mp3 in [*matches]:
            speaker=speakers[mp3]
            mco=matches[mp3]
            print(f"{speaker}|cno_cwl/{mp3}|{mco}", file=file)
    
        