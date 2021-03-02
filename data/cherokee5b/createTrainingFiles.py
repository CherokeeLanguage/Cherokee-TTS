#!/usr/bin/env python3
import os
import sys
import unicodedata as ud
import random
import json
from shutil import rmtree
import pathlib

if __name__ == "__main__":
	
	langSkip:list=["zh"]
	
	workdir:str = os.path.dirname(sys.argv[0])
	if workdir.strip() != "":
		os.chdir(workdir)
	workdir = os.getcwd()
	
	for file in ["train.txt", "val.txt", "all.txt"]:
		if os.path.exists(file):
			os.remove(file)
	
	for _ in ["lin_spectrograms", "mel_spectrograms"]:
		rmtree(os.path.join(workdir, _), ignore_errors=True)
		
	speaker_counts:dict=dict()
		
	for parent in [ "../comvoi_clean",
		 			#"../cherokee-audio/beginning-cherokee",
					#"../cherokee-audio/cherokee-language-coach-1",
					#"../cherokee-audio/cherokee-language-coach-2",
					"../cherokee-audio/durbin-feeling",
					"../cherokee-audio/michael-conrad",
					#"../cherokee-audio/sam-hider",
					#"../cherokee-audio/see-say-write",
					"../cherokee-audio/thirteen-moons",
					"../cherokee-audio/cno",
					"../cherokee-audio/tacotron-2020-12-28",
					]:
		for txt in ("all.txt", "val.txt", "train.txt"):
			with open(pathlib.Path(parent).joinpath(txt), "r") as f:
				lines:list = []
				for line in f:
					fields=line.split("|")
					if fields[2] in langSkip:
						continue
					line=ud.normalize("NFD",line.strip())
					line=line.replace("|wav/", "|"+parent+"/wav/")
					lines.append(line)
					speaker:str=fields[1].strip()
					if speaker not in speaker_counts:
						speaker_counts[speaker]=0
					speaker_counts[speaker]=speaker_counts[speaker]+1
					
				random.Random(len(lines)).shuffle(lines)
				with open(txt, "a") as t:
					for line in lines:
						t.write(line)
						t.write("\n")
				
	print(f"Speakers {len(speaker_counts):,}")
	speakers = [*speaker_counts]
	speakers.sort()
	for speaker in speakers:
		if "cno" not in speaker and "chr" not in speaker:
			continue
		print(f"   CHR Speaker {speaker}: {speaker_counts[speaker]:,}")
	
	#get char listing needed for params file
	letters=""
	chars:list=[]
	with open("all.txt", "r") as f:
		for line in f:
			fields=line.split("|")
			text:str=fields[6].lower()
			text=ud.normalize("NFD", text)
			for c in text:
				if c in "!\"',.?@&-()*^%$#;":
					continue
				if c in chars:
					continue
				chars.append(c)
		chars.sort()
		for c in chars:
			letters+=str(c)
		config:dict=dict()
		config["characters"]=letters
		tmp=json.dumps(config, ensure_ascii=False, sort_keys=True, indent=3)
		with open("json-characters.json", "w") as f:
			f.write(tmp)
			f.write("\n")
		
	#rewrite shuffled
	lines=[]
	with open("train.txt", "r") as t:
		for line in t:
			lines.append(line)
	random.Random(len(lines)).shuffle(lines)
	with open("train.txt", "w") as t:
		for line in lines:
			t.write(line)
	
	#rewrite shuffled
	lines=[]
	with open("val.txt", "r") as v:
		for line in v:
			lines.append(line)
	random.Random(len(lines)).shuffle(lines)
	with open("val.txt", "w") as v:
		for line in lines:
			v.write(line)
	
	sys.exit()
