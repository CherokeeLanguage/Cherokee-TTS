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

workdir:str = os.path.dirname(sys.argv[0])
if workdir.strip() != "":
	os.chdir(workdir)
workdir = os.getcwd()

#cleanup any previous runs
for parent in [".", "../cherokee-audio/sam-hider", "../cherokee", "../comvoi_clean"]:
	for dir in ["linear_spectrograms", "spectrograms"]:
	    rmtree(os.path.join(parent, dir), ignore_errors=True)

for file in ["train.txt", "val.txt"]:
	if os.path.exists(file):
		os.remove(file)

with open("ma-split-annotated.txt", "r") as f:
	lines:list = []
	for line in f:
		line=line.strip()
		line=line.replace("|durbin-feeling|", "|01-chr|")
		line=line.replace("|ma-split/", "|../cherokee/ma-split/")
		lines.append(line)
	random.Random(0).shuffle(lines)
	size=len(lines)
	trainSize=int((size*95/100))
	with open("train.txt", "a") as t:
		for line in lines[:trainSize]:
			t.write(line)
			t.write("\n")
	with open("val.txt", "a") as t:
		for line in lines[trainSize:]:
			t.write(line)
			t.write("\n")
			
lines:list = []
with open("../cherokee-audio/sam-hider/all.txt", "r") as f:
	for line in f:
		line=line.strip()
		line=line.replace("|wav/", "|../cherokee-audio/sam-hider/wav/")
		lines.append(line)
	random.Random(0).shuffle(lines)
	size=len(lines)
	trainSize=int((size*95/100))
	with open("train.txt", "a") as t:
		for line in lines[:trainSize]:
			t.write(line)
			t.write("\n")
	with open("val.txt", "a") as t:
		for line in lines[trainSize:]:
			t.write(line)
			t.write("\n")

#Common Voice Data
commonVoice:list=[]
with open("../comvoi_clean/all.txt") as f:
	for line in f:
		line=line.strip()
		fields=line.split("|")
		recno:str=fields[0]
		speaker:str=fields[1]
		language:str=fields[2]
		wav:str=fields[3]
		text:str=fields[4]
		commonVoice.append(f"{recno}|{speaker}-{language}|{language}|../comvoi_clean/{wav}|||{text}|")

	random.Random(0).shuffle(commonVoice)
	size=len(commonVoice)
	trainSize=int((size*95/100))
	with open("train.txt", "a") as t:
		for line in commonVoice[:trainSize]:
			t.write(line)
			t.write("\n")
	with open("val.txt", "a") as t:
		for line in commonVoice[trainSize:]:
			t.write(line)
			t.write("\n")

femaleVoices:list=["14-de", "51-de", "02-fr", "04-fr", "14-fr", "18-fr", "19-fr", "22-fr", "03-ru"]

while len(femaleVoices) < 21:
	temp = femaleVoices.copy()
	for v in temp:
		femaleVoices.append(v)

#We don't shuffle the female donor voices to prevent training issues

for i in range(3,21):
	voice:str=femaleVoices[i]
	donorLines = [s for s in commonVoice if "|"+voice+"|" in s]
	random.Random(i).shuffle(donorLines)
	with open("train.txt", "a") as t:
		fields=donorLines[0].split("|")
		recno:str=fields[0]
		speaker:str=fields[1]
		language:str=fields[2]
		wav:str=fields[3]
		text:str=fields[6]
		#convert vowel orthography of non-Cherokee text shoved in as a placeholder to something different
		for vix, c in enumerate("aeiouv"):
			text=ud.normalize("NFD", text)
			text=text.replace(c, f"{vix:d}")
		#intentionally wanting text to remain in NFD form.
		t.write(f"{recno}|{i:02d}-chr|chr|{wav}|||{text}|")
		t.write("\n")
	with open("val.txt", "a") as v:
		fields=donorLines[1].split("|")
		recno:str=fields[0]
		speaker:str=fields[1]
		language:str=fields[2]
		wav:str=fields[3]
		text:str=fields[6]
		#convert vowel orthography of non-Cherokee text shoved in as a placeholder to something different
		for vix, c in enumerate("aeiouv"):
			text=ud.normalize("NFD", text)
			text=text.replace(c, f"{vix:d}")
		#intentionally wanting text to remain in NFD form.
		v.write(f"{recno}|{i:02d}-chr|chr|{wav}|||{text}|")
		v.write("\n")

random.Random(i).shuffle(lines)
with open("train.txt", "a") as t:
	line=lines[0].replace("|02-chr", "|01-syn-chr")
	t.write(line)
	t.write("\n")
with open("val.txt", "a") as v:
	line=lines[1].replace("|02-chr", "|01-syn-chr")
	v.write(line)
	v.write("\n")

#rewrite shuffled
lines=[]
with open("train.txt", "r") as t:
	for line in t:
		lines.append(line)
random.Random(1).shuffle(lines)
with open("train.txt", "w") as t:
	for line in lines:
		t.write(line)

#rewrite shuffled
lines=[]
with open("val.txt", "r") as v:
	for line in v:
		lines.append(line)
random.Random(1).shuffle(lines)
with open("val.txt", "w") as v:
	for line in lines:
		v.write(line)

sys.exit()
