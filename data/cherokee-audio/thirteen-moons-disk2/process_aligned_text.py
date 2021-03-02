#!/usr/bin/env python3

if __name__ == "__main__":

    import os
    import sys
    import unicodedata as ud

    aligned_text: str = "text-copyrighted/aligned-text.txt"
    output_text: str = "thirteen-moons-selected.txt"

    workdir: str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()

    from os import walk

    mp3s:list = []
    for (dirpath, dirnames, filenames) in os.walk("mp3"):
        mp3s.extend(filenames)
        break
    mp3s.sort()
    print(f"Loaded {len(mp3s):,} MP3s")

    lines:list = []
    with open(aligned_text, "r") as f:
        for line in f:
            if len(line.strip())==0:
                break
            lines.append(line.strip())
    print(f"Loaded {len(lines):,} text aligments")

    count:int=0
    with open(output_text, "w") as f:
        line_no:int=0
        for mp3, line in zip(mp3s, lines):
            line_no+=1
            line = line.strip()
            mp3 = mp3.replace("mp3/", "")
            if "|" in line:
                parts:list = line.split("|")
                if len(parts)!=2:
                    continue
                if parts[1].strip() != mp3:
                    raise Exception(f"Alignment fail [{line_no}] mp3={mp3} marker={parts[1]} text={parts[0]}")
            if "XXX" in line:
                continue
            print(f"?|mp3/{mp3}|{line}", file=f)
            count+=1

    print(f"Output {count:,} {aligned_text} entries")