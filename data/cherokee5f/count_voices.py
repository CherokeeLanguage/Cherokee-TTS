#!/usr/bin/env python3

import os
import sys
import unicodedata as ud
import random
import json
from shutil import rmtree
import pathlib
import re

if __name__ == "__main__":
    
    workdir:str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()
    
    voice_counts:dict = dict()
    
    with open("all.txt", "r") as f:
        for line in f:
            fields = line.split("|")
            if len(fields) < 2:
                continue
            voice = fields[1]
            if not voice in voice_counts.keys():
                voice_counts[voice]=0
            voice_counts[voice] = voice_counts[voice] + 1
            
    counts_list:list = list()
    for key in voice_counts.keys():
        counts_list.append((key, voice_counts[key]))
    
    counts_list.sort(key=lambda value: value[1], reverse=True)
    
    counter:int = 0
    for idx in range(len(counts_list)):
        count = counts_list[idx]
        if "cno-" in count[0] or "-chr" in count[0]:
            continue
        print(count)
        counter += 1
        if counter >= 3:
            break

    voices:set = set()
    with open("train.txt", "r") as f:
        for line in f:
            fields = line.split("|")
            voice = fields[1]
            if voice in voices:
                continue
            voices.add(voice)

    with open("voices.inc", "w") as f:
        for voice_count in counts_list:
            voice:str = voice_count[0]
            if not voice in voices:
                continue
            f.write("\"")
            f.write(voice)
            f.write("\"")
            f.write(" ")
        f.write("\n")

    with open("voices.txt", "w") as f:
        for voice_count in counts_list:
            voice:str = voice_count[0]
            if not voice in voices:
                continue
            f.write(voice)
            f.write("\n")

    with open("voices-xchr.inc", "w") as f:
        for voice_count in counts_list:
            voice:str = voice_count[0]
            if not voice in voices:
                continue
            if "-chr" in voice:
                continue
            f.write("\"")
            f.write(voice)
            f.write("\"")
            f.write(" ")
        f.write("\n")

    with open("voices-xchr.txt", "w") as f:
        for voice_count in counts_list:
            voice:str = voice_count[0]
            if not voice in voices:
                continue
            if "-chr" in voice:
                continue
            f.write(voice)
            f.write("\n")

    with open("voices-chr.inc", "w") as f:
        for voice_count in counts_list:
            voice:str = voice_count[0]
            if not voice in voices:
                continue
            if not "-chr" in voice:
                continue
            f.write("\"")
            f.write(voice)
            f.write("\"")
            f.write(" ")
        f.write("\n")

    with open("voices-chr.txt", "w") as f:
        for voice_count in counts_list:
            voice:str = voice_count[0]
            if not voice in voices:
                continue
            if not "-chr" in voice:
                continue
            f.write(voice)
            f.write("\n")
        
        
                                              