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

comvoiIgnore:list=["fr", "nl", "ru", "zh"]

workdir:str = os.path.dirname(sys.argv[0])
if workdir.strip() != "":
	os.chdir(workdir)
workdir = os.getcwd()

for file in ["train.txt", "val.txt", "all.txt"]:
	if os.path.exists(file):
		os.remove(file)

for parent in [ "../cherokee-audio/beginning-cherokee",
				"../cherokee-audio/cherokee-language-coach-1",
				"../cherokee-audio/cherokee-language-coach-2",
				"../cherokee-audio/durbin-feeling",
				"../cherokee-audio/michael-conrad",
				"../cherokee-audio/sam-hider"
				]:
	for dir in ["linear_spectrograms", "spectrograms"]:
	    rmtree(os.path.join(parent, dir), ignore_errors=True)
	with open(parent + "/all.txt", "r") as f:
		lines:list = []
		for line in f:
			line=ud.normalize("NFC",line.strip())
			line=line.replace("|wav/", "|"+parent+"/wav/")
			lines.append(line)
		random.Random(1).shuffle(lines)
		size=len(lines)
		trainSize=int((size*90/100))
		with open("train.txt", "a") as t:
			for line in lines[:trainSize]:
				t.write(line)
				t.write("\n")
		with open("val.txt", "a") as t:
			for line in lines[trainSize:]:
				t.write(line)
				t.write("\n")
		with open("all.txt", "a") as t:
			for line in lines:
				t.write(line)
				t.write("\n")

#Common Voice Data
for dir in ["linear_spectrograms", "spectrograms"]:
    rmtree(os.path.join("../comvoi_clean", dir), ignore_errors=True)
commonVoice:list=[]
with open("../comvoi_clean/all.txt") as f:
	for line in f:
		line=line.strip()
		fields=line.split("|")
		recno:str=fields[0]
		speaker:str=fields[1]
		language:str=fields[2]
		wav:str=fields[3]
		if language in comvoiIgnore:
			#don't put unused languages in train and val files.
			#even though the training process ignores the entries
			#the spectrogram preprocessing step does not ignore them.
			continue
		text:str=ud.normalize("NFD",fields[4]) #use decomposed diactrics for donor voices
		commonVoice.append(f"{recno}|{speaker}-{language}|{language}|../comvoi_clean/{wav}|||{text}|")

	random.Random(2).shuffle(commonVoice)
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
	with open("all.txt", "a") as t:
		for line in commonVoice:
			t.write(line)
			t.write("\n")

#rewrite shuffled
lines=[]
with open("train.txt", "r") as t:
	for line in t:
		lines.append(line)
random.Random(4).shuffle(lines)
with open("train.txt", "w") as t:
	for line in lines:
		t.write(line)

#rewrite shuffled
lines=[]
with open("val.txt", "r") as v:
	for line in v:
		lines.append(line)
random.Random(5).shuffle(lines)
with open("val.txt", "w") as v:
	for line in lines:
		v.write(line)

sys.exit()