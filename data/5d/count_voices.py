
from typing import Set

import os
import sys
import unicodedata as ud
import random
import json
from shutil import rmtree
import pathlib
import re
from typing import Dict

if __name__ == "__main__":

    workdir: str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()

    voice_counts: dict = dict()
    voice_counts_by_lang: Dict[str, Set] = dict()

    with open("all.txt", "r") as f:
        for line in f:
            fields = line.split("|")
            if len(fields) < 2:
                continue
            voice: str = fields[1]
            if voice not in voice_counts.keys():
                voice_counts[voice] = 0
            voice_counts[voice] = voice_counts[voice] + 1
            lang: str = fields[2]
            if lang not in voice_counts_by_lang.keys():
                voice_counts_by_lang[lang] = set()
            voice_counts_by_lang[lang].add(voice)

    with open("voice-counts-by-language.txt", "w") as f:
        for lang in sorted(list(voice_counts_by_lang.keys())):
            count: int = len(voice_counts_by_lang[lang])
            print(f"{lang}:{count:,}", file=f)

    counts_list: list = list()
    for key in voice_counts.keys():
        counts_list.append((key, voice_counts[key]))

    counts_list.sort(key=lambda value: value[1], reverse=True)

    counter: int = 0
    for idx in range(len(counts_list)):
        count = counts_list[idx]
        if "cno-" in count[0] or "-chr" in count[0]:
            continue
        print(count)
        counter += 1
        if counter >= 3:
            break

    voices: set = set()
    with open("train.txt", "r") as f:
        for line in f:
            fields = line.split("|")
            voice = fields[1]
            if voice in voices:
                continue
            voices.add(voice)

    with open("voices.inc", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
            if not voice in voices:
                continue
            f.write("\"")
            f.write(voice)
            f.write("\"")
            f.write(" ")
        f.write("\n")

    with open("voices.txt", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
            if not voice in voices:
                continue
            f.write(voice)
            f.write("\n")

    with open("voices-xchr.inc", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
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
            voice: str = voice_count[0]
            if not voice in voices:
                continue
            if "-chr" in voice:
                continue
            f.write(voice)
            f.write("\n")

    with open("voices-chr.inc", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
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
            voice: str = voice_count[0]
            if not voice in voices:
                continue
            if not "-chr" in voice:
                continue
            f.write(voice)
            f.write("\n")
