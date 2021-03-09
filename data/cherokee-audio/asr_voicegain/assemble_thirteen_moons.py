#!/usr/bin/env python3

import os
import sys
import shutil
import unicodedata as ud
import random

from pydub import AudioSegment

if __name__ == "__main__":

    if sys.argv[0].strip() != "":
        os.chdir(os.path.dirname(sys.argv[0]))

    src_dir_base = os.path.join(os.getcwd(), "..", "thirteen-moons-disk")

    subdir: str
    for subdir in ["mp3", "txt", "mp3-test", "txt-test"]:
        shutil.rmtree(subdir, ignore_errors=True)
        os.mkdir(subdir)

    # 000001|10-chr|chr|wav/0009-1-02 D01 Track 02-019895.wav|||ᎧᎵ ᎠᏂᏅ ᏗᎦᏅᎯᏓ ᏗᎦᏍᎩᎶᎩ, ᏗᏂᏲᏟ ᎡᏓᏍᏘ ᎠᏂᏅ|

    idx: int = 0
    entries: list = list()
    for disk_no in range(1, 6):
        src_dir = src_dir_base + str(disk_no)

        with open(os.path.join(src_dir, "all.txt"), "r") as f:
            for line in f:
                idx += 1
                parts: list = line.split("|")
                wav = parts[3]
                txt = parts[6]
                entries.append((f"{idx:09d}", os.path.join(src_dir, wav), ud.normalize("NFD", txt)))

    print(f"Loaded {len(entries):,} entries with audio and text.")

    random.Random(1234).shuffle(entries)

    # create train/test sets
    train_size: int = int(len(entries) * .94)

    print("Creating mp3s")
    print()

    os.truncate("train.txt", 0)
    os.truncate("test.txt", 0)

    totalLength: float = 0
    idx: int
    wav: str
    text: str
    for idx, wav, text in entries[:train_size]:
        mp3: str = os.path.join("mp3", os.path.splitext(os.path.basename(wav))[0].replace(" ", "_") + ".mp3")
        txt: str = os.path.join("txt", os.path.splitext(os.path.basename(wav))[0].replace(" ", "_") + ".txt")
        text: str = ud.normalize('NFD', text)
        audio: AudioSegment = AudioSegment.from_file(wav)
        audio.set_channels(1)
        audio.set_frame_rate(22050)
        audio.export(mp3, format="mp3", parameters=["-qscale:a", "0"])
        with open(txt, "w") as w:
            print(text, file=w)
        totalLength += audio.duration_seconds
        with open("train.txt", "a") as f:
            print(f"{int(idx):09d}|{mp3}|{text}", file=f)

    minutes = int(totalLength / 60)
    hours = int(minutes / 60)
    minutes = minutes % 60
    seconds = int(totalLength % 60 + 0.5)
    print(f"Total train duration: {hours:,}:{minutes:02}:{seconds:02}")

    totalLength = 0
    idx: int
    wav: str
    text: str
    for idx, wav, text in entries[train_size:]:
        mp3: str = os.path.join("mp3-test", os.path.splitext(os.path.basename(wav))[0].replace(" ", "_") + ".mp3")
        txt: str = os.path.join("txt-test", os.path.splitext(os.path.basename(wav))[0].replace(" ", "_") + ".txt")
        text: str = ud.normalize('NFD', text)
        audio: AudioSegment = AudioSegment.from_file(wav)
        audio.set_channels(1)
        audio.set_frame_rate(22050)
        audio.export(mp3, format="mp3", parameters=["-qscale:a", "0"])
        with open(txt, "w") as w:
            print(text, file=w)
        totalLength += audio.duration_seconds
        with open("test.txt", "a") as f:
            print(f"{int(idx):09d}|{mp3}|{text}", file=f)

    minutes = int(totalLength / 60)
    hours = int(minutes / 60)
    minutes = minutes % 60
    seconds = int(totalLength % 60 + 0.5)
    print(f"Total test duration: {hours:,}:{minutes:02}:{seconds:02}")
    print()

    sys.exit()
