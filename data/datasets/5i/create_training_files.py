import subprocess

from typing import List

import re

import json
import os
import pathlib
import random
import sys
import unicodedata as ud
from shutil import rmtree


def main():
    workdir: str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()

    punctuations_out = '、。，"(),.:;¿?¡!\\'
    punctuations_in = '\'-'

    for file in ["train.txt", "val.txt", "all.txt"]:
        if os.path.exists(file):
            os.remove(file)

    for _ in ["lin_spectrograms", "mel_spectrograms"]:
        rmtree(os.path.join(workdir, _), ignore_errors=True)

    speaker_counts: dict = dict()

    for parent in [  #
            "../../other-audio-data/comvoi_clean",  #
            "../../other-audio-data/cstr-vctk-american",  #
            # "../../cherokee-audio-data-private/beginning-cherokee",  #
            # "../../cherokee-audio-data-private/cherokee-language-coach-1",  #
            # "../../cherokee-audio-data-private/cherokee-language-coach-2",  #
            # "../../cherokee-audio-data-private/durbin-feeling",  #
            "../../cherokee-audio-data/durbin-feeling-tones",  #
            # "../../cherokee-audio-data/michael-conrad",  #
            "../../cherokee-audio-data/michael-conrad2",  #
            # "../../cherokee-audio-data-private/sam-hider",  #
            # "../../cherokee-audio-data/see-say-write",  #
            # "../../cherokee-audio-data-private/thirteen-moons-disk1",  #
            # "../../cherokee-audio-data-private/thirteen-moons-disk2",  #
            # "../../cherokee-audio-data-private/thirteen-moons-disk3",  #
            # "../../cherokee-audio-data-private/thirteen-moons-disk4",  #
            # "../../cherokee-audio-data-private/thirteen-moons-disk5",  #
            # "../../cherokee-audio-data/cno",  #
            "../../cherokee-audio-data/walc-1",  #
            # "../../cherokee-audio-data/wwacc",  #
            # "../../cherokee-audio-data-synthetic/tacotron-2020-12-28",  #
    ]:
        for txt in ["all.txt", "val.txt", "train.txt"]:
            with open(pathlib.Path(parent).joinpath(txt), "r") as f:
                lines: list = []
                for line in f:
                    fields = line.split("|")
                    speaker: str = fields[1].strip()
                    line = ud.normalize("NFC", line.strip())
                    line = line.replace("|wav/", "|" + parent + "/wav/")
                    lines.append(line)
                    if txt == "all.txt":
                        if speaker not in speaker_counts:
                            speaker_counts[speaker] = 0
                        speaker_counts[speaker] = speaker_counts[speaker] + 1

                random.Random(len(lines)).shuffle(lines)
                with open(txt, "a") as t:
                    line: str
                    for line in lines:
                        fields: List[str] = line.split("|")
                        good: bool = True
                        for bad_char in "0123456789&@":
                            if bad_char in fields[6]:
                                good = False
                                break
                        if good:
                            t.write(line)
                            t.write("\n")

    with open("speaker-counts.txt", "w") as f:
        print(file=f)
        print(f"Total speakers {len(speaker_counts):,}", file=f)
        print(file=f)
        speakers = [*speaker_counts]
        speakers.sort()
        for speaker in speakers:
            print(f"   Speaker {speaker}: {speaker_counts[speaker]:,}", file=f)

    # get char listing needed for params file
    letters = ""
    chars: list = []
    with open("all.txt", "r") as f:
        for line in f:
            fields = line.split("|")
            text: str = fields[6].lower()
            text = ud.normalize("NFC", text)
            for c in text:
                if c in punctuations_in or c in punctuations_out:
                    continue
                if c in chars:
                    continue
                chars.append(c)
        chars.sort()
        for c in chars:
            letters += str(c)
        config: dict = dict()
        config["characters"] = letters
        tmp = json.dumps(config, ensure_ascii=False, sort_keys=True, indent=3)
        with open("json-characters.json", "w") as j:
            j.write(tmp)
            j.write("\n")

    # rewrite shuffled
    lines = []
    with open("train.txt", "r") as t:
        for line in t:
            lines.append(line)
    random.Random(len(lines)).shuffle(lines)
    with open("train.txt", "w") as t:
        for line in lines:
            t.write(line)

    # rewrite shuffled
    lines = []
    with open("val.txt", "r") as v:
        for line in v:
            lines.append(line)
    random.Random(len(lines)).shuffle(lines)
    with open("val.txt", "w") as v:
        for line in lines:
            v.write(line)

    subprocess.run(["python", "count_langs.py"], check=True)
    subprocess.run(["python", "count_voices.py"], check=True)
    sys.exit()


if __name__ == "__main__":
    main()
