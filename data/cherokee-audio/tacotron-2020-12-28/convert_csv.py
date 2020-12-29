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
    
    if (sys.argv[0].strip()!=""):
            os.chdir(os.path.dirname(sys.argv[0]))
            
    rmtree("selected", ignore_errors=True)
    os.mkdir("selected")
    
    source_csv:str="AudioQualityVotes.csv"
    dest_txt:str="AudioQualityVotes.txt"
    
    source_data:dict=dict()
    dest_data:list=list()
    
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
            
            if ranking<0.5:
                continue
            if votes<1:
                continue
            
            copy(file, dest_file)
            
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
            
            line=voice+"|"+dest_file+"|"+txt
            dest_data.append(line)
    
            
    with open(dest_txt, "w") as file:
        for line in dest_data:
            print(line, file=file)