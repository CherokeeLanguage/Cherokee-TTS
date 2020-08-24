#!/usr/bin/env python3
import os
import sys
import string
import unicodedata as ud
import random
import re
import pathlib
import subprocess
from shutil import rmtree

from md2pdf.core import md2pdf

os.chdir(os.path.dirname(sys.argv[0]))

rmtree("wav", ignore_errors=True)
pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)

with open("sam-hider.txt", "r") as f:
    entries: list = []
    for line in f:
        mp3: str=line.split("|")[0].strip()
        text: str=ud.normalize("NFD", line.split("|")[1].strip())
        entries.append((mp3,text))

for mp3, text in entries:
    wav:str="wav/"+os.path.splitext(os.path.basename(mp3))[0]+".wav"
    text:str=ud.normalize('NFC', text)
    subprocess.run(["ffmpeg","-i",mp3,"-ac","1","-ar","22050",wav], check=True)
    
sys.exit()
