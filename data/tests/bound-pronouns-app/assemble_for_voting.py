#!/usr/bin/env python3
import os
import progressbar
import shutil
import typing
from pydub import AudioSegment
from pydub.effects import normalize
import sys

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    speakers: typing.List[str] = ["299-en-f", "311-en-m", "334-en-m", "339-en-f", "345-en-m"]
    master_file: str = "review-sheet.txt"

    # ID|PSET|VSET|PRONOUN|VERB|GENDER|SYLLABARY|PRONOUNCE|ANSWER|FILENAME

    entries: typing.List[typing.Tuple[str, str]] = list()

    with open(master_file, "r") as f:
        for line in f:
            if "|" not in line:
                continue
            if line.strip().startswith("#"):
                continue
            fields = line.strip().split("|")
            if len(fields) < 10:
                continue
            record_id: str = fields[0].strip()
            if record_id == "ID":
                continue
            syllabary: str = fields[6].strip()
            pronounce: str = fields[7].strip()
            english: str = fields[8].strip()
            mp3_name: str = fields[9].strip()

            text: str = f"{syllabary} ({pronounce})\n{english}"
            entries.append((mp3_name, text))

    shutil.rmtree("tmp", ignore_errors=True)
    os.mkdir("tmp")

    print(f"Processing {len(speakers):,d} speakers with {len(entries):,d} entries per speaker.")
    bar = progressbar.ProgressBar(maxval=len(entries)*len(speakers))
    bar.start()
    for (base_name, text) in entries:
        speaker: str
        for speaker in speakers:
            bar.update(bar.currval + 1)
            src_mp3 = os.path.join(f"bound-pronouns-app-{speaker}", f"{base_name}.mp3")
            dest_mp3 = os.path.join(f"tmp", f"{speaker}-{base_name}-bound-pronouns-app.mp3")
            dest_txt = os.path.join(f"tmp", f"{speaker}-{base_name}-bound-pronouns-app.txt")
            if not os.path.isfile(src_mp3):
                print(f"Missing MP3 {src_mp3}")
                continue
            audio: AudioSegment = AudioSegment.from_file(src_mp3)
            audio = audio.set_channels(1).set_frame_rate(22050)
            audio = normalize(audio)
            audio.export(dest_mp3, format="mp3", parameters=["-qscale:a", "3"])
            with open(dest_txt, "w") as w:
                w.write(f"[{speaker}]\n{text}\n")
    bar.finish()

    rsync: str = "rsync --delete-before -a --verbose --progress --human-readable tmp/ " \
                 "clcom@vhost.cherokeelessons.com:/home/AudioQualityVote/audio/ "
    os.system(rsync)

    sys.exit(0)
