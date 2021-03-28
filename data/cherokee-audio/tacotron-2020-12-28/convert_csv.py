#!/usr/bin/env python3

import os
import sys
import csv
import unicodedata as ud
import random
import re
from shutil import rmtree
from shutil import copy

if __name__ == "__main__":
    
    minVotes:int=1
    minQuality:float=1
    
    if (sys.argv[0].strip()!=""):
            os.chdir(os.path.dirname(sys.argv[0]))
            
    rmtree("selected", ignore_errors=True)
    os.mkdir("selected")
    
    source_csv:str="AudioQualityVotes.csv"
    dest_txt:str="AudioQualityVotes.txt"
    bad_txt:str="AudioQualityVotes-bad.txt"
    
    source_data:dict=dict()
    dest_data:list=list()
    dest_bad_data: list = list()

    bad_count: int = 0
    count:int=0
    with open(source_csv, newline='') as csvfile:
        rows = csv.DictReader(csvfile)
        for row in rows:
            id:int=int(row["Id"])
            ranking:float=float(row["Ranking"])
            votes:int=int(row["Votes"])
            txt:str=ud.normalize("NFD", row["Text"])
            txt=txt.strip()
            file:str="audio"+row["File"]
            dest_file:str="selected/"+f"{id:06}"+"-"+os.path.basename(file)
            
            voice:str=""
            
            if votes<minVotes:
                continue
            
            if "cno-spk_0" in file:
                voice="cno-spk_0"
            elif "cno-spk_1" in file:
                voice="cno-spk_1"
            elif "cno-spk_2" in file:
                voice="cno-spk_2"
            elif "cno-spk_3" in file:
                voice="cno-spk_3"
            else:
                voice="?"

            if ranking<minQuality:
                bad_count += 1
                dest_bad_data.append(txt)
                continue
            else:
                count += 1
                copy(file, dest_file)
                line:str = voice+"|"+dest_file+"|"+txt
                dest_data.append(line)
    
    print(f"Total good entries {count:,}.")
    print(f"Total bad entries {bad_count:,}.")

    random.Random(len(dest_data)).shuffle(dest_data)
    with open(dest_txt, "w") as file:
        for line in dest_data:
            print(line, file=file)

    random.Random(len(dest_bad_data)).shuffle(dest_bad_data)
    with open(bad_txt, "w") as file:
        buffer:str=""
        for line in dest_bad_data:
            if not line[-1] in ";,.?!\"'":
                line += "."
            if len(buffer) > 0 and len(buffer) + len(line) + 1 > 60:
                print(buffer, file=file)
                buffer = line[0].upper()+line[1:]
            else:
                if buffer:
                    buffer += " "
                buffer += line[0].upper()+line[1:]
        if buffer:
            print(buffer, file=file)