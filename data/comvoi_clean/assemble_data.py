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

    max_length: float = 10.0

    if sys.argv[0].strip() != "":
        os.chdir(os.path.dirname(sys.argv[0]))

    max_duration: float = 10.0
    output_text: str = "comvoi-all.txt"

    # cleanup any previous runs
    for folder in ["mp3"]:
        rmtree(folder, ignore_errors=True)
    pathlib.Path(".").joinpath("mp3").mkdir(exist_ok=True)

    entries: list = list()

    for lang in ["de", "fr", "nl", "ru", "zh"]:
        with open(pathlib.Path.joinpath(lang, "meta.csv")) as f:
            for line in f:
                fields = line.split("|")
                speaker = fields[0] + "-" + lang
                wav = fields[1]
                audio = pathlib.Path.joinpath(lang, "wav", wav)
                text = ud.normalize('NFD', fields[2])
                mp3 = pathlib.Path.joinpath("mp3", wav.replace(".wav", ".mp3"))
                entries.append((audio, speaker, mp3, text))

    print(f"Loaded {len(entries):,} entries.")

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
    for wav, speaker, mp3, text in entries:
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

        audio: AudioSegment = wav_segment[diaz_start:diaz_end]
        audio = effects.normalize(audio)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(22050)
        audio.export(mp3, format="mp3", parameters=["-qscale:a", "3"])
        totalLength += audio.duration_seconds
        if shortestLength < 0 or shortestLength > audio.duration_seconds:
            shortestLength = audio.duration_seconds
        if longestLength < audio.duration_seconds:
            longestLength = audio.duration_seconds
        idx += 1
        rows.append(f"{idx:06d}|{speaker}|{lang}|{mp3}|||{text}|")

    bar.finish()

    with open("assemble-stats.txt", "w") as f:
        print(f"Output {idx:,} entries.", file=f)

        print(file=f)

        totalLength = int(totalLength)
        minutes = int(totalLength / 60)
        seconds = int(totalLength % 60)
        print(f"Total duration: {minutes:,}:{seconds:02}", file=f)

        shortestLength = int(shortestLength)
        minutes = int(shortestLength / 60)
        seconds = int(shortestLength % 60)
        print(f"Shortest duration: {minutes:,}:{seconds:02}", file=f)

        longestLength = int(longestLength)
        minutes = int(longestLength / 60)
        seconds = int(longestLength % 60)
        print(f"Longest duration: {minutes:,}:{seconds:02}", file=f)

        print(file=f)

    print("Creating final output file")
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
