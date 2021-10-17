from glob import glob

import sys

import array

import os

import numpy
from torch import Tensor


def main():
    import torch
    import soundfile as sf
    from univoc import Vocoder

    cwd: str = os.getcwd()

    # download pretrained weights (and optionally move to GPU)
    vocoder: Vocoder = Vocoder.from_pretrained(
            "https://github.com/bshall/UniversalVocoding/releases/download/v0.2/univoc-ljspeech-7mtpaq.pt").cuda()

    npy_file: str
    for npy_file in glob("*.npy"):

        wav_file = npy_file.replace(".npy", ".wav")
        npy_name: str = os.path.basename(npy_file)

        print(f"Vocoding {npy_name}")

        # load log-Mel spectrogram from file or from tts (see https://github.com/bshall/Tacotron for example)
        mel_npy: array = numpy.load(npy_name).transpose()
        top_db = 80
        mel_npy = numpy.maximum(mel_npy, -top_db)
        mel_npy = mel_npy / top_db
        mel_tensor: Tensor = torch.FloatTensor(mel_npy).unsqueeze(0).to("cuda")

        # generate and save waveform
        with torch.no_grad():
            wav, sr = vocoder.generate(mel_tensor)
            sf.write(wav_file, wav, sr)


if __name__ == "__main__":
    main()
