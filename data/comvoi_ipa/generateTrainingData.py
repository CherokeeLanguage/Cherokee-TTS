#!/usr/bin/env python3
import os
import pathlib
import random
import sys
import unicodedata as ud
from builtins import list
from shutil import rmtree

import progressbar
import pydub.effects as effects
from phonemizer import phonemize
from pydub import AudioSegment

from split_audio import detect_sound

mark_all_as_ipa: bool = True
ipa_to_mco: bool = False


def as_mco(text: str) -> str:
    macron_lower = "\u0331"
    text = text.replace("ː", ":")
    text = text.replace("v", "v" + macron_lower)
    text = text.replace("ʌ", "v")
    return text


if __name__ == "__main__":

    src_dir: str = "../comvoi_clean"

    os.chdir(os.path.dirname(sys.argv[0]))

    MASTER_TEXT: str = src_dir + "/comvoi-clean.txt"
    max_duration: float = 10.0

    rmtree("wav", ignore_errors=True)
    pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)
    langs: set = set()

    espeak_langs: dict = dict()

    espeak_langs["de"] = "de"
    espeak_langs["fr"] = "fr-fr"
    espeak_langs["nl"] = "nl"
    espeak_langs["ru"] = "ru"
    espeak_langs["zh"] = "cmn"

    num_lines: int = 0
    with open(MASTER_TEXT, "r") as f:
        num_lines = sum(1 for line in f)

    bar = progressbar.ProgressBar(maxval=num_lines)
    bar.start()

    with open(MASTER_TEXT, "r") as f:
        entries: dict = {}
        idx: int = 0
        for line in f:
            idx += 1
            bar.update(idx)
            fields = line.split("|")
            xid: str = fields[0].strip()
            spkr: str = fields[1].strip()
            lang: str = fields[2].strip()
            mp3: str = fields[3].strip()

            text: str = ud.normalize("NFC", fields[6].strip())
            # print(f"{idx:09d}: {text}")
            text = phonemize(text, language=espeak_langs[lang], backend="espeak", preserve_punctuation=True,
                             with_stress=True, language_switch="remove-flags")

            if ipa_to_mco:
                text = as_mco(text)

            text = ud.normalize("NFD", text)

            if text == "":
                continue
            dedupeKey = spkr + "|" + text

            if mark_all_as_ipa:
                lang = "ipa"

            entries[dedupeKey] = (xid, spkr, lang, mp3, text)
            langs.add(lang)
    bar.finish()

    print(f"Loaded {len(entries):,} entries with audio and text.")

    bar = progressbar.ProgressBar(maxval=len(entries))
    bar.start()
    shortestLength: float = -1
    longestLength: float = 0.0
    totalLength: float = 0.0
    print("Creating wavs")
    rows: list = []
    idx = 0
    for xid, speaker, lang, mp3, text in entries.values():
        idx += 1
        bar.update(idx)
        wav: str = "wav/" + os.path.splitext(os.path.basename(mp3))[0] + ".wav"
        text: str = ud.normalize('NFD', text)
        mp3_segment: AudioSegment = AudioSegment.from_file(src_dir + "/" + mp3)
        segments: list = detect_sound(mp3_segment)
        if len(segments) > 1:
            mp3_segment = mp3_segment[segments[0][0]:segments[-1][1]]
        if mp3_segment.duration_seconds > max_duration:
            continue
        audio: AudioSegment = AudioSegment.silent(125, 22050)
        audio = audio.append(mp3_segment, crossfade=0)
        audio = audio.append(AudioSegment.silent(125, 22050))
        audio = effects.normalize(audio)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(22050)
        audio.export(wav, format="wav")
        totalLength += audio.duration_seconds
        if shortestLength < 0 or shortestLength > audio.duration_seconds:
            shortestLength = audio.duration_seconds
        if longestLength < audio.duration_seconds:
            longestLength = audio.duration_seconds
        rows.append(f"{xid}|{speaker}|{lang}|{wav}|||{text}|")
    bar.finish()

    totalLength = int(totalLength)
    minutes = int(totalLength / 60)
    seconds = int(totalLength % 60)
    print(f"Total duration: {minutes:,}:{seconds:02}")

    shortestLength = int(shortestLength)
    minutes = int(shortestLength / 60)
    seconds = int(shortestLength % 60)
    print(f"Shortest duration: {minutes:,}:{seconds:02}")

    longestLength = int(longestLength)
    minutes = int(longestLength / 60)
    seconds = int(longestLength % 60)
    print(f"Longest duration: {minutes:,}:{seconds:02}")

    print("Creating training files")

    # save all copy before shuffling
    with open("all.txt", "w") as f:
        for line in rows:
            f.write(line)
            f.write("\n")

    with open("train.txt", "w") as f:
        f.write("")
    with open("val.txt", "w") as f:
        f.write("")

    for lang in langs:
        subset: list = list()
        for row in rows:
            rlang = row.split("|")[2]
            if rlang != lang:
                continue
            subset.append(row)
        print(f" {lang} length: {len(subset):,}")
        random.Random(len(subset)).shuffle(subset)
        # create train/val sets - splitting up data by language evenly
        trainSize: int = (int)(len(subset) * .95)
        valSize: int = len(subset) - trainSize
        with open("train.txt", "a") as f:
            for line in subset[:trainSize]:
                f.write(line)
                f.write("\n")

        with open("val.txt", "a") as f:
            for line in subset[trainSize:]:
                f.write(line)
                f.write("\n")
        print(f"  Train size for {lang}: {trainSize}")
        print(f"   Val size for {lang}: {valSize}")

    print(f"All size: {len(rows)}")
    print("Folder:", pathlib.Path(".").resolve().name)

    sys.exit()
