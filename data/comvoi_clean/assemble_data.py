#!/usr/bin/env python3
import os
import pathlib
import sys
import unicodedata as ud
import warnings
from builtins import list
from shutil import rmtree

import progressbar
import pydub.effects as effects
import torch.hub
from pydub import AudioSegment

if __name__ == "__main__":

    warnings.filterwarnings("ignore")

    diaz_pipeline = torch.hub.load('pyannote/pyannote-audio', 'dia', device="cpu")

    skip_speakers: set = set()  # speakers to skip due to audio quality issues (hums, etc)

    if sys.argv[0].strip() != "" and os.path.dirname(sys.argv[0]) != "":
        os.chdir(os.path.dirname(sys.argv[0]))

    max_duration: float = 10.0
    output_text: str = "comvoi-all.txt"

    # cleanup any previous runs
    for folder in ["mp3"]:
        rmtree(folder, ignore_errors=True)
    pathlib.Path(".").joinpath("mp3").mkdir(exist_ok=True)

    entries: list = list()
    bad_entries: list = list()

    for lang in ["de", "fr", "nl", "ru", "zh"]:
        with open(pathlib.Path(".").joinpath(lang, "meta.csv")) as f:
            idx: int = 0
            for line in f:
                idx += 1
                fields = line.split("|")
                speaker_no = fields[0]
                speaker = speaker_no + "-" + lang
                if speaker in skip_speakers:
                    continue
                wav = fields[1]
                audio = pathlib.Path(".").joinpath(lang, "wavs", speaker_no, wav)
                text = ud.normalize('NFD', fields[2]).strip()
                mp3 = pathlib.Path(".").joinpath("mp3", f"{lang}-{speaker}-{idx:09d}.mp3")
                if os.path.exists(audio):
                    entries.append((audio, speaker, lang, mp3, text))
                else:
                    bad_entries.append((audio, speaker, lang, mp3, text))

    print(f"Skipped {len(bad_entries):,} bad entries.")
    print(f"Loaded {len(entries):,} entries.")

    with open("bad-entries.txt", "w") as f:
        idx: int = 0
        for wav, speaker, lang, mp3, text in bad_entries:
            idx += 1
            f.write(f"{idx:06d}|{speaker}|{lang}|{wav}|||{text}|")
            f.write("\n")

    bar = progressbar.ProgressBar(maxval=len(entries))
    bar.start()
    idx: int = 0
    count: int = 0
    lang: str = "en"
    shortestLength: float = -1
    longestLength: float = 0.0
    totalLength: float = 0.0
    print("Creating mp3s")
    rows: list = []
    for wav, speaker, lang, mp3, text in entries:
        bar.update(count)
        count += 1
        text: str = ud.normalize('NFD', text)
        wav_segment: AudioSegment = AudioSegment.from_file(wav)
        wav_segment = effects.normalize(wav_segment)

        diaz_start: int = len(wav_segment)
        diaz_end: int = 0
        diaz = diaz_pipeline({"audio": wav})
        for turn, _, _ in diaz.itertracks(yield_label=True):
            ts = int(turn.start * 1000 - 10)
            if ts < 0:
                ts = 0
            te = int(turn.end * 1000 + 10)
            if te > len(wav_segment):
                te = len(wav_segment)
            if ts < diaz_start:
                diaz_start = ts
            if te > diaz_end:
                diaz_end = te
        if diaz_end < diaz_start:
            continue
        if diaz_end - diaz_start < 500:
            diaz_start = 0
            diaz_end = len(wav_segment)

        audio: AudioSegment = wav_segment[diaz_start:diaz_end]
        audio = effects.normalize(audio)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(22050)
        audio.export(mp3, format="mp3", parameters=["-q:a", "3"])
        totalLength += audio.duration_seconds
        if shortestLength < 0 or shortestLength > audio.duration_seconds:
            shortestLength = audio.duration_seconds
        if longestLength < audio.duration_seconds:
            longestLength = audio.duration_seconds
        idx += 1
        rows.append(f"{idx:06d}|{speaker}|{lang}|{mp3}|||{text}|")

    bar.finish()

    with open("assemble-stats.txt", "w") as f:
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

    with open(output_text, "w") as f:
        for line in rows:
            f.write(line)
            f.write("\n")

    with open("assemble-stats.txt", "a") as f:
        print(f"All size: {len(rows)}", file=f)
        print(file=f)
        print("Folder:", pathlib.Path(".").resolve().name, file=f)
        print(file=f)

    print("done")
    sys.exit()
