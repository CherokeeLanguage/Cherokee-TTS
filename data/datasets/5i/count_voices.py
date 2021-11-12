from typing import List

from typing import Dict
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
from typing import Set

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
        total_voice_count: int = 0
        for lang in sorted(list(voice_counts_by_lang.keys())):
            count: int = len(voice_counts_by_lang[lang])
            total_voice_count += count
            print(f"{lang}:{count:,}", file=f)
        print(file=f)
        print(f"Total:{total_voice_count:,}", file=f)
        print(file=f)

    counts_list: list = list()
    for key in voice_counts.keys():
        counts_list.append((key, voice_counts[key]))

    counts_list.sort(key=lambda value: value[1], reverse=True)

    voices_by_lang: Dict[str, List[str]] = dict()
    voices: set = set()
    with open("train.txt", "r") as f:
        for line in f:
            fields = line.split("|")
            voice = fields[1]
            lang = fields[2]
            if lang not in voices_by_lang.keys():
                voices_by_lang[lang] = list()
            if voice not in voices_by_lang[lang]:
                voices_by_lang[lang].append(voice)
            if voice not in voices:
                voices.add(voice)

    with open("voices.inc", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
            if voice not in voices:
                continue
            f.write("\"")
            f.write(voice)
            f.write("\"")
            f.write(" ")
        f.write("\n")

    with open("voices.inc.py", "w") as f:
        f.write("voices: typing.List[str] = [")
        for voice_count in counts_list:
            voice: str = voice_count[0]
            if voice not in voices:
                continue
            f.write("\"")
            f.write(voice)
            f.write("\"")
            f.write(", ")
        f.write("]\n")
        for lang in voices_by_lang.keys():
            var_lang: str = re.sub("(?i)[^a-z_]", "_", lang)
            lang_voices: List[str] = voices_by_lang[lang]
            lang_voices.sort()

            f.write("\n")
            f.write(f"# {var_lang} {len(lang_voices)}\n")
            f.write(f"voices_{var_lang}: typing.List[str] = [")

            for voice in lang_voices:
                f.write("\"")
                f.write(voice)
                f.write("\"")
                f.write(", ")
            f.write("]\n")

    with open("voices.txt", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
            if voice not in voices:
                continue
            f.write(voice)
            f.write("\n")

    with open("voices-with-counts.txt", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
            count: int = voice_count[1]
            if voice not in voices:
                continue
            f.write(f"{voice}={count:,}")
            f.write("\n")

    with open("voices-xchr.inc", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
            if voice not in voices:
                continue
            if "-chr" in voice or "-walc1" in voice:
                continue
            f.write("\"")
            f.write(voice)
            f.write("\"")
            f.write(" ")
        f.write("\n")

    with open("voices-xchr.txt", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
            if voice not in voices:
                continue
            if "-chr" in voice or "-walc1" in voice:
                continue
            f.write(voice)
            f.write("\n")

    with open("voices-chr.inc", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
            if voice not in voices:
                continue
            if "-chr" not in voice and "-walc1" not in voice:
                continue
            f.write("\"")
            f.write(voice)
            f.write("\"")
            f.write(" ")
        f.write("\n")

    with open("voices-chr.inc.py", "w") as f:
        f.write("voices: list[str] = [")
        for voice_count in counts_list:
            voice: str = voice_count[0]
            if voice not in voices:
                continue
            if "-chr" not in voice and "-walc1" not in voice:
                continue
            f.write("\"")
            f.write(voice)
            f.write("\"")
            f.write(", ")
        f.write("]\n")


    with open("voices-chr.txt", "w") as f:
        for voice_count in counts_list:
            voice: str = voice_count[0]
            if voice not in voices:
                continue
            if "-chr" not in voice and "-walc1" not in voice:
                continue
            f.write(voice)
            f.write("\n")
