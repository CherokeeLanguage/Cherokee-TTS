import typing

import json

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
from typing import Tuple


def cd_script_dir() -> None:
    if sys.argv[0].strip():
        dir_name: str = os.path.dirname(sys.argv[0])
        if dir_name:
            os.chdir(dir_name)


def main():
    cd_script_dir()

    mp3_set_title: str = "The Two Bragging Hunters"
    mp3_copyright_by: str = "Michael Conrad"
    mp3_encoded_by: str = "Michael Conrad"
    mp3_copy_year: str = str(datetime.date.today().year)
    mp3_from_gl: bool = False  # Use Griffin-Lim audio and don't vocode if True
    use_gpu: bool = True
    
    tts_weights_glob: str = "5h*"
    # tts_weights_glob: str = "*"
    

    # fr 22
    voices_fr: typing.List[str] = ["01-fr", "02-fr", "04-fr", "05-fr", "06-fr", "07-fr", "08-fr", "09-fr", "10-fr",
                                   "11-fr", "13-fr", "14-fr", "15-fr", "16-fr", "17-fr", "18-fr", "19-fr", "20-fr",
                                   "21-fr", "22-fr", "25-fr", "26-fr", ]

    # en 29
    voices_en: typing.List[str] = ["294-en-f", "297-en-f", "299-en-f", "300-en-f",
                                   "301-en-f", "305-en-f", "306-en-f", "308-en-f", "310-en-f", "311-en-m", "318-en-f",
                                   "329-en-f", "330-en-f", "333-en-f", "334-en-m", "339-en-f", "341-en-f", "345-en-m",
                                   "360-en-m", "361-en-f", "362-en-f", ]

    # ru 6
    voices_ru: typing.List[str] = ["01-ru", "02-ru", "03-ru", "04-ru", "05-ru", "06-ru", ]

    # de 39
    voices_de: typing.List[str] = ["01-de", "02-de", "04-de", "05-de", "06-de", "07-de", "09-de", "10-de", "11-de",
                                   "12-de", "13-de", "14-de", "17-de", "19-de", "21-de", "22-de", "23-de", "24-de",
                                   "25-de", "26-de", "27-de", "29-de", "31-de", "32-de", "33-de", "36-de", "37-de",
                                   "40-de", "41-de", "43-de", "44-de", "45-de", "46-de", "47-de", "48-de", "49-de",
                                   "50-de", "51-de", "52-de", ]

    # chr 22
    voices_chr: typing.List[str] = ["01-f-walc1", "01-m-df-chr", "01-m-ssw-chr", "01-m-walc1", "01-m-wwacc", "02-chr",
                                    "02-f-walc1", "02-m-df-chr", "02-m-walc1", "03-chr", "03-f-walc1", "04-chr",
                                    "04-f-walc1", "04-m-walc1", "05-f-walc1", "06-f-walc1", "cno-f-chr_1",
                                    "cno-f-chr_2", "cno-f-chr_3", "cno-f-chr_5", "cno-m-chr_1", "cno-m-chr_2", ]

    # voices CNO
    voices_chr_cno: typing.List[str] = ["cno-f-chr_2", "cno-f-chr_3", "cno-f-chr_5", "cno-m-chr_1", "cno-m-chr_2"]

    # chr_syl 1
    voices_chr_syl: typing.List[str] = ["10-chr", ]

    # nl 11
    voices_nl: typing.List[str] = ["01-nl", "02-nl", "03-nl", "04-nl", "06-nl", "07-nl", "08-nl", "09-nl", "10-nl",
                                   "11-nl", "12-nl", ]

    # zh 6
    voices_zh: typing.List[str] = ["01-zh", "02-zh", "03-zh", "05-zh", "06-zh", "07-zh", ]

    voices = voices_en
    voices.sort()

    # voices: List[str] = ["299-en-f", "318-en-f", "339-en-f", "311-en-m", "334-en-m", "345-en-m", "360-en-m"]

    # voices: List[str] = ["cno-f-chr_2", "cno-m-chr_2", "02-m-df-chr", "01-m-df-chr", "cno-m-chr_1", "cno-f-chr_5",
    #                     "cno-f-chr_3", "cno-f-chr_1", ]

    # voices: List[str] = ["02-ru", "04-fr", "05-ru", "27-de", "11-fr", "13-de"]
    
    text_file: str = "bragging-hunter-mco.txt"    

    cp_folder: str = os.path.join(os.getcwd(), "..", "..", "..", "checkpoints", tts_weights_glob)
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

        if not mp3_from_gl:
            if use_gpu:
                cmd_list = ["python", "wavernnx.py"]
            else:
                cmd_list = ["python", "wavernnx-cpu.py"]
            # cmd_list=["python", "diffwave_vocoder.py"]
            subprocess.run(cmd_list)

        durations: List[Tuple[str, str]] = list()
        output_mp3_path: str = f"bragging_hunter_{voice}_mp3"
        os.mkdir(f"bragging_hunter_{voice}_mp3")
        for ix in range(len(text_list)):
            from_wav: str
            if mp3_from_gl:
                from_wav = f"{ix + 1}.wav"
            else:
                from_wav = f"wg-{ix + 1}.wav"
            to_mp3 = os.path.join(output_mp3_path, f"{ix + 1:03d}.mp3")
            audio: AudioSegment = AudioSegment.from_file(from_wav)
            audio = audio.set_channels(2)
            audio = audio.set_frame_rate(44100)
            audio = effects.normalize(audio)

            durations.append((to_mp3, audio.duration_seconds))

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
            if not mp3_from_gl:
                os.remove(from_wav)
        with open(os.path.join(output_mp3_path, f"durations-{voice}.json"), "w") as w:
            json.dump(durations, w, indent=2)


if __name__ == "__main__":
    main()
