#!/usr/bin/env python3
import json
import os
import pathlib
import random
import re
import sys
import unicodedata as ud
from shutil import rmtree

with_syllabary: bool = False
only_syllabary: bool = False
include_o_form: bool = False

if __name__ == "__main__":

    langSkip: set = {"chr-syl", "ru", "zh"}
    speakerSkip: set = {
            # "239-en", "264-en", "250-en", "259-en", "247-en", "261-en",
            "263-en", "283-en",
            "286-en", "274-en", "276-en", "270-en", "277-en", "281-en", "231-en", "238-en",
            "271-en", "257-en", "273-en", "284-en", "360-en", "308-en", "374-en", "329-en",
            "340-en", "334-en", "351-en", "361-en", "317-en", "311-en", "287-en", "314-en",
            "310-en", "294-en", "330-en", "323-en", "347-en", "362-en", "266-en", "304-en",
            "339-en", "313-en", "333-en", "305-en", "318-en", "244-en", "316-en", "335-en",
            "307-en", "363-en", "295-en", "336-en", "312-en", "267-en", "275-en", "297-en",
            "258-en", "288-en", "232-en", "272-en", "301-en", "292-en", "278-en", "280-en",
            "341-en", "268-en", "279-en", "299-en", "298-en", "285-en", "326-en", "300-en",
            "345-en", "254-en", "269-en", "230-en", "293-en", "252-en", "262-en", "243-en",
            "227-en", "343-en", "229-en", "255-en", "240-en", "253-en", "248-en", "233-en",
            "282-en", "27-de", "228-en", "251-en", "234-en", "246-en", "260-en", "226-en",
            "245-en", "241-en", "11-fr", "303-en", "306-en", "265-en", "237-en", "249-en",
    }

    workdir: str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()

    if not with_syllabary and only_syllabary:
        print("Can't do without Syllabary while outputting only Syllabary!")
        sys.exit(-1)

    for file in ["train.txt", "val.txt", "all.txt"]:
        if os.path.exists(file):
            os.remove(file)

    for _ in ["lin_spectrograms", "mel_spectrograms"]:
        rmtree(os.path.join(workdir, _), ignore_errors=True)

    speaker_counts: dict = dict()

    for parent in ["../comvoi_clean",  #
                   "../cstr-vctk-corpus",  #
                   "../cherokee-audio/beginning-cherokee",  #
                   "../cherokee-audio/cherokee-language-coach-1",  #
                   "../cherokee-audio/cherokee-language-coach-2",  #
                   "../cherokee-audio/durbin-feeling",  #
                   "../cherokee-audio/michael-conrad",  #
                   "../cherokee-audio/michael-conrad2",  #
                   "../cherokee-audio/sam-hider",  #
                   "../cherokee-audio/see-say-write",  #
                   "../cherokee-audio/thirteen-moons-disk1",  #
                   "../cherokee-audio/thirteen-moons-disk2",  #
                   "../cherokee-audio/thirteen-moons-disk3",  #
                   "../cherokee-audio/thirteen-moons-disk4",  #
                   "../cherokee-audio/thirteen-moons-disk5",  #
                   "../cherokee-audio/cno",  #
                   # "../cherokee-audio/tacotron-2020-12-28",  #
                   ]:
        for txt in ["all.txt", "val.txt", "train.txt"]:
            with open(pathlib.Path(parent).joinpath(txt), "r") as f:
                lines: list = []
                for line in f:
                    fields = line.split("|")
                    speaker: str = fields[1].strip()
                    if speaker in speakerSkip:
                        continue
                    lang: str = fields[2]
                    if lang in langSkip:
                        continue
                    line = ud.normalize("NFD", line.strip())
                    if lang == "chr":
                        if not include_o_form and "\u030a" in line:
                            continue
                        if not with_syllabary and re.search("(?i)[Ꭰ-Ᏼ]", line):
                            continue
                        if only_syllabary and not re.search("(?i)[Ꭰ-Ᏼ]", line):
                            continue
                    line = line.replace("|wav/", "|" + parent + "/wav/")
                    lines.append(line)
                    if txt == "all.txt":
                        if speaker not in speaker_counts:
                            speaker_counts[speaker] = 0
                        speaker_counts[speaker] = speaker_counts[speaker] + 1

                random.Random(len(lines)).shuffle(lines)
                with open(txt, "a") as t:
                    for line in lines:
                        t.write(line)
                        t.write("\n")

    print()
    print(f"Speakers {len(speaker_counts):,}")
    print()
    speakers = [*speaker_counts]
    speakers.sort()
    for speaker in speakers:
        if "cno" not in speaker and "chr" not in speaker:
            continue
        print(f"   CHR Speaker {speaker}: {speaker_counts[speaker]:,}")

    # get char listing needed for params file
    letters = ""
    chars: list = []
    with open("all.txt", "r") as f:
        for line in f:
            fields = line.split("|")
            text: str = fields[6].lower()
            text = ud.normalize("NFD", text)
            for c in text:
                # if c in "!\"',.?@&-()*^%$#;":
                #    continue
                if c in chars:
                    continue
                chars.append(c)
        chars.sort()
        for c in chars:
            letters += str(c)
        config: dict = dict()
        config["characters"] = letters
        tmp = json.dumps(config, ensure_ascii=False, sort_keys=True, indent=3)
        with open("json-characters.json", "w") as f:
            f.write(tmp)
            f.write("\n")

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

    sys.exit()
