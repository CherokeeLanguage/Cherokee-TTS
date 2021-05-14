#!/usr/bin/env python3
import os
import pathlib
import random
import re
import sys
import unicodedata as ud
from builtins import list
from shutil import rmtree

import progressbar
import pydub.effects as effects
from phonemizer import phonemize
from pydub import AudioSegment

from split_audio import detect_sound

mark_all_as_ipa: bool = False
ipa_to_mco: bool = True


def as_mco(string: str) -> str:
    macron_lower = "\u0331"
    macron = "\u0304"
    mco_glottal_stop = "ɂ"
    ipa_glottal_stop = "ʔ"
    ipa_long_vowel = "ː"
    string = ud.normalize("NFD", string)
    string = string.replace(ipa_glottal_stop, mco_glottal_stop)
    string = string.replace(ipa_long_vowel, ":")
    string = re.sub("(?i)(v)", "\\1" + macron_lower, string)
    string = string.replace("ʌ", "v" + macron)
    string = re.sub("(?i)j", "y", string)
    string = re.sub("(?i)dʒ", "j", string)
    string = re.sub("(?i)tʃ", "ch", string)
    # text = re.sub("(?i)ɑ", "a", text)
    string = re.sub("(?i)([aeiou])", "\\1" + macron, string)
    return string


if __name__ == "__main__":

    src_dir: str = "../cstr-vctk-corpus"

    if os.path.dirname(sys.argv[0]) != "":
        os.chdir(os.path.dirname(sys.argv[0]))

    MASTER_TEXT: str = src_dir + "/cstr-vctk-corpus.txt"
    max_duration: float = 10.0

    rmtree("wav", ignore_errors=True)
    pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)
    langs: set = set()

    espeak_langs: dict = dict()

    espeak_langs["de"] = "de"
    espeak_langs["en"] = "en-gb" # default if english speaker not in voice langs lookup table
    espeak_langs["fr"] = "fr-fr"
    espeak_langs["nl"] = "nl"
    espeak_langs["ru"] = "ru"
    espeak_langs["zh"] = "cmn"

    espeak_voice_langs: dict = dict()
    espeak_voice_langs["225-en"] = "en-gb"
    espeak_voice_langs["226-en"] = "en-gb"
    espeak_voice_langs["227-en"] = "en-gb"
    espeak_voice_langs["228-en"] = "en-gb"
    espeak_voice_langs["229-en"] = "en-gb"
    espeak_voice_langs["230-en"] = "en-gb"
    espeak_voice_langs["231-en"] = "en-gb"
    espeak_voice_langs["232-en"] = "en-gb"
    espeak_voice_langs["233-en"] = "en-gb"
    espeak_voice_langs["234-en"] = "en-gb-scotland"
    espeak_voice_langs["236-en"] = "en-gb"
    espeak_voice_langs["237-en"] = "en-gb-scotland"
    espeak_voice_langs["238-en"] = "en-gb-scotland"
    espeak_voice_langs["239-en"] = "en-gb"
    espeak_voice_langs["240-en"] = "en-gb"
    espeak_voice_langs["241-en"] = "en-gb-scotland"
    espeak_voice_langs["243-en"] = "en-gb"
    espeak_voice_langs["244-en"] = "en-gb"
    espeak_voice_langs["245-en"] = "en-gb-scotland"
    espeak_voice_langs["246-en"] = "en-gb-scotland"
    espeak_voice_langs["247-en"] = "en-gb-scotland"
    espeak_voice_langs["248-en"] = "en-gb"
    espeak_voice_langs["249-en"] = "en-gb-scotland"
    espeak_voice_langs["250-en"] = "en-gb"
    espeak_voice_langs["251-en"] = "en-gb"
    espeak_voice_langs["252-en"] = "en-gb-scotland"
    espeak_voice_langs["253-en"] = "en-gb"
    espeak_voice_langs["254-en"] = "en-gb"
    espeak_voice_langs["255-en"] = "en-gb-scotland"
    espeak_voice_langs["256-en"] = "en-gb"
    espeak_voice_langs["257-en"] = "en-gb"
    espeak_voice_langs["258-en"] = "en-gb"
    espeak_voice_langs["259-en"] = "en-gb"
    espeak_voice_langs["260-en"] = "en-gb-scotland"
    espeak_voice_langs["261-en"] = "en-gb-scotland"
    espeak_voice_langs["262-en"] = "en-gb-scotland"
    espeak_voice_langs["263-en"] = "en-gb-scotland"
    espeak_voice_langs["264-en"] = "en-gb-scotland"
    espeak_voice_langs["265-en"] = "en-gb-scotland"
    espeak_voice_langs["266-en"] = "en-gb-scotland"
    espeak_voice_langs["267-en"] = "en-gb"
    espeak_voice_langs["268-en"] = "en-gb"
    espeak_voice_langs["269-en"] = "en-gb"
    espeak_voice_langs["270-en"] = "en-gb"
    espeak_voice_langs["271-en"] = "en-gb-scotland"
    espeak_voice_langs["272-en"] = "en-gb-scotland"
    espeak_voice_langs["273-en"] = "en-gb"
    espeak_voice_langs["274-en"] = "en-gb"
    espeak_voice_langs["275-en"] = "en-gb-scotland"
    espeak_voice_langs["276-en"] = "en-gb"
    espeak_voice_langs["277-en"] = "en-gb"
    espeak_voice_langs["278-en"] = "en-gb"
    espeak_voice_langs["279-en"] = "en-gb"
    espeak_voice_langs["281-en"] = "en-gb-scotland"
    espeak_voice_langs["282-en"] = "en-gb"
    espeak_voice_langs["283-en"] = "en-gb-scotland"
    espeak_voice_langs["284-en"] = "en-gb-scotland"
    espeak_voice_langs["285-en"] = "en-gb-scotland"
    espeak_voice_langs["286-en"] = "en-gb"
    espeak_voice_langs["287-en"] = "en-gb"
    espeak_voice_langs["288-en"] = "en-gb-scotland"
    espeak_voice_langs["292-en"] = "en-gb-scotland"
    espeak_voice_langs["293-en"] = "en-gb-scotland"
    espeak_voice_langs["294-en"] = "en-us"
    espeak_voice_langs["295-en"] = "en-gb-scotland"
    espeak_voice_langs["297-en"] = "en-us"
    espeak_voice_langs["298-en"] = "en-gb-scotland"
    espeak_voice_langs["299-en"] = "en-us"
    espeak_voice_langs["300-en"] = "en-us"
    espeak_voice_langs["301-en"] = "en-us"
    espeak_voice_langs["302-en"] = "en-us"
    espeak_voice_langs["303-en"] = "en-us"
    espeak_voice_langs["304-en"] = "en-gb-scotland"
    espeak_voice_langs["305-en"] = "en-us"
    espeak_voice_langs["306-en"] = "en-us"
    espeak_voice_langs["307-en"] = "en-us"
    espeak_voice_langs["308-en"] = "en-us"
    espeak_voice_langs["310-en"] = "en-us"
    espeak_voice_langs["311-en"] = "en-us"
    espeak_voice_langs["312-en"] = "en-us"
    espeak_voice_langs["313-en"] = "en-gb-scotland"
    espeak_voice_langs["314-en"] = "en-gb"
    espeak_voice_langs["315-en"] = "en-us"
    espeak_voice_langs["316-en"] = "en-us"
    espeak_voice_langs["317-en"] = "en-us"
    espeak_voice_langs["318-en"] = "en-us"
    espeak_voice_langs["323-en"] = "en-gb"
    espeak_voice_langs["326-en"] = "en-gb"
    espeak_voice_langs["329-en"] = "en-us"
    espeak_voice_langs["330-en"] = "en-us"
    espeak_voice_langs["333-en"] = "en-us"
    espeak_voice_langs["334-en"] = "en-us"
    espeak_voice_langs["335-en"] = "en-gb"
    espeak_voice_langs["336-en"] = "en-gb"
    espeak_voice_langs["339-en"] = "en-us"
    espeak_voice_langs["340-en"] = "en-gb-scotland"
    espeak_voice_langs["341-en"] = "en-us"
    espeak_voice_langs["343-en"] = "en-us"
    espeak_voice_langs["345-en"] = "en-us"
    espeak_voice_langs["347-en"] = "en-gb"
    espeak_voice_langs["351-en"] = "en-gb-scotland"
    espeak_voice_langs["360-en"] = "en-us"
    espeak_voice_langs["361-en"] = "en-us"
    espeak_voice_langs["362-en"] = "en-us"
    espeak_voice_langs["363-en"] = "en-us"
    espeak_voice_langs["364-en"] = "en-gb-scotland"
    espeak_voice_langs["374-en"] = "en-gb"
    espeak_voice_langs["376-en"] = "en-gb"

    num_lines: int = 0
    with open(MASTER_TEXT, "r") as f:
        num_lines = sum(1 for line in f)

    print("Converting to IPA")

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

            espeak_lang: str
            if spkr in espeak_voice_langs:
                espeak_lang = espeak_voice_langs[spkr]
            else:
                espeak_lang = espeak_langs[lang]
            text = phonemize(text, language=espeak_lang, backend="espeak", preserve_punctuation=True,
                             with_stress=True, language_switch="remove-flags")

            text = ud.normalize("NFD", text)

            if ipa_to_mco:
                text = as_mco(text)

            if text == "":
                continue

            dedupeKey = spkr + "|" + text + "|" + mp3

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
        audio = audio.append(AudioSegment.silent(125, 22050), crossfade=0)
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

    with open("stats.txt", "w") as f:
        print(f"Output {len(rows):,} entries.", file=f)

        print(file=f)

        totalLength = int(totalLength)
        hours = int(totalLength / 3600)
        minutes = int(totalLength % 3600 / 60)
        seconds = int(totalLength % 60)
        print(f"Total duration: {hours:,}:{minutes:02}:{seconds:02}", file=f)

        shortestLength = int(shortestLength)
        minutes = int(shortestLength / 60)
        seconds = int(shortestLength % 60)
        print(f"Shortest duration: {minutes:,}:{seconds:02}", file=f)

        longestLength = int(longestLength)
        minutes = int(longestLength / 60)
        seconds = int(longestLength % 60)
        print(f"Longest duration: {minutes:,}:{seconds:02}", file=f)

        print(file=f)

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
        trainSize: int = (int)(len(subset) * .90)
        valSize: int = len(subset) - trainSize
        with open("train.txt", "a") as f:
            for line in subset[:trainSize]:
                f.write(line)
                f.write("\n")

        with open("val.txt", "a") as f:
            for line in subset[trainSize:]:
                f.write(line)
                f.write("\n")

    with open("stats.txt", "a") as f:
        print(f"All size: {len(rows):,}", file=f)
        print(f"Train size: {trainSize:,}", file=f)
        print(f"Val size: {valSize:,}", file=f)
        print(file=f)
        print("Folder:", pathlib.Path(".").resolve().name, file=f)
        print(file=f)

    sys.exit()
