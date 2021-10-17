import datetime
import glob
import os
import shutil
import subprocess
import sys
import unicodedata as ud

from pydub import AudioSegment
from pydub import effects
from typing import List


def main():
    mp3_set_title: str = "The Two Bragging Hunters"
    mp3_copyright_by: str = "Michael Conrad"
    mp3_encoded_by: str = "Michael Conrad"
    mp3_copy_year: str = str(datetime.date.today().year)

    voices: List[str] = ["360-en-m", "329-en-f", "361-en-f", "308-en-f", "311-en-m", "334-en-m"]

    #voices: List[str] = ["cno-f-chr_2", "cno-m-chr_2", "02-m-df-chr", "01-m-df-chr", "cno-m-chr_1", "cno-f-chr_5",
    #                     "cno-f-chr_3", "cno-f-chr_1", ]

    #voices: List[str] = ["02-ru", "04-fr", "05-ru", "27-de", "11-fr", "13-de"]
    
    text_file: str = "bragging-hunter-mco.txt"
    use_gpu: bool = True

    if sys.argv[0].strip():
        dir_name: str = os.path.dirname(sys.argv[0])
        if dir_name:
            os.chdir(dir_name)

    cp_folder: str = os.path.join(os.getcwd(), "..", "..", "..", "checkpoints", "*")
    print(cp_folder)
    _: list = []
    for checkpoint_file in glob.glob(cp_folder):
        _.append(checkpoint_file)
    # cp_file:str = os.path.basename(sorted(_, key=os.path.getmtime)[-1])
    cp_file: str = os.path.realpath(sorted(_, key=os.path.getmtime)[-1])
    cp_name: str = os.path.basename(cp_file)
    synthesize_bin = os.path.join(os.getcwd(), "..", "..", "..", "synthesize.py")

    print(f"Using checkpoint {cp_name}.")

    shutil.rmtree("npy", ignore_errors=True)
    shutil.rmtree("wav", ignore_errors=True)
    path: str
    for path in glob.glob("bragging_hunter_*_mp3"):
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
    for path in glob.glob("*.wav"):
        os.remove(path)
    for path in glob.glob("*.npy"):
        os.remove(path)

    text_list: List[str] = []
    with open(text_file) as r:
        line: str
        for line in r:
            text_list.append(ud.normalize("NFC", line.strip()))

    for voice in voices:
        text_pipe: str = ""
        print(f"Generating audio for {voice}")
        for ix in range(len(text_list)):
            line = text_list[ix]
            text_pipe += f"{ix + 1}|{line}|{voice}|chr\n"

        cmd_list: List[str] = ["python", synthesize_bin, "--output", os.getcwd(), "--save_spec", "--checkpoint",
                               cp_file]
        if not use_gpu:
            cmd_list.append("--cpu")

        subprocess.run(cmd_list, input=text_pipe, text=True)

        if use_gpu:
            cmd_list = ["python", "wavernnx.py"]
        else:
            cmd_list = ["python", "wavernnx-cpu.py"]

        subprocess.run(cmd_list)

        os.mkdir(f"bragging_hunter_{voice}_mp3")
        for ix in range(len(text_list)):
            from_wav = f"wg-{ix + 1}.wav"
            to_mp3 = os.path.join(f"bragging_hunter_{voice}_mp3", f"{ix + 1:03d}.mp3")
            audio: AudioSegment = AudioSegment.from_file(from_wav)
            audio = audio.set_channels(2)
            audio = audio.set_frame_rate(44100)
            audio = effects.normalize(audio)

            id3v2_tags: dict = dict()
            id3v2_tags["COMM"] = cp_name
            id3v2_tags["TALB"] = mp3_set_title + f" ({voice})"
            id3v2_tags["TCON"] = "Speech"
            id3v2_tags["TCOP"] = "CC BY-SA"
            id3v2_tags["TDRC"] = mp3_copy_year
            id3v2_tags["TENC"] = mp3_encoded_by
            id3v2_tags["TIT2"] = text_list[ix]
            id3v2_tags["TLAN"] = "chr"
            id3v2_tags["TOWN"] = mp3_copyright_by
            id3v2_tags["TPE1"] = voice
            id3v2_tags["TRCK"] = f"{ix + 1}/{len(text_list)}"
            id3v2_tags["USLT"] = text_list[ix]

            audio.export(to_mp3, format="mp3", tags=id3v2_tags, parameters=["-qscale:a", "3"])

            os.remove(f"{ix + 1}.wav")
            os.remove(f"{ix + 1}.npy")
            os.remove(from_wav)


if __name__ == "__main__":
    main()
