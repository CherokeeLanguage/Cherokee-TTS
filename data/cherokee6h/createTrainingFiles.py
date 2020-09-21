#!/usr/bin/env python3
import os
import sys
import unicodedata as ud
import random
from shutil import rmtree
import pathlib

workdir:str = os.path.dirname(sys.argv[0])
if workdir.strip() != "":
	os.chdir(workdir)
workdir = os.getcwd()

for file in ["train.txt", "val.txt", "all.txt"]:
	if os.path.exists(file):
		os.remove(file)

for _ in ["lin_spectrograms", "mel_spectrograms"]:
	rmtree(os.path.join(workdir, _), ignore_errors=True)
	
allEntries:list=list()
train:list = list()
val:list = list()
for parent in [ "../cherokee-audio/beginning-cherokee",
				"../cherokee-audio/cherokee-language-coach-1",
				"../cherokee-audio/cherokee-language-coach-2",
				"../cherokee-audio/durbin-feeling",
				"../cherokee-audio/michael-conrad",
				"../cherokee-audio/sam-hider"
				]:
	lines:list=list()
	with open(parent + "/all.txt", "r") as f:		
		for line in f:
			line=ud.normalize("NFC",line.strip())
			line=line.replace("|wav/", "|"+parent+"/wav/")
			lines.append(line)
			
		allEntries.extend(lines)
		
		size=len(lines)
		random.Random(size).shuffle(lines)
		trainSize=int((size*95/100))
		
		train.extend(lines[:trainSize])
		val.extend(lines[trainSize:])
		
random.Random(len(train)).shuffle(train)
random.Random(len(val)).shuffle(val)

with open("train.txt", "a") as t:
	for line in train:
		t.write(line)
		t.write("\n")
with open("val.txt", "a") as t:
	for line in val:
		t.write(line)
		t.write("\n")
with open("all.txt", "a") as t:
	for line in allEntries:
		t.write(line)
		t.write("\n")
		
print(f"All entries: {len(allEntries)}")
print(f"Train entries: {len(train)}")
print(f"Val entries: {len(val)}")
print("Folder:",pathlib.Path(".").resolve().name)

sys.exit()
