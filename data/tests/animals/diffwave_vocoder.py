import glob

import progressbar
from progressbar import ProgressBar
from torch import Tensor
from typing import List

import numpy
import os
import sys
import torch
import torchaudio
from diffwave.inference import predict as diffwave_predict


def cd_script_dir() -> None:
    if sys.argv[0].strip():
        dir_name: str = os.path.dirname(sys.argv[0])
        if dir_name:
            os.chdir(dir_name)


def main():
    cd_script_dir()
    model_dir = "diffwave-ljspeech-22kHz-1000578.pt"
    npy_files: List[str] = list()
    npy_files.extend(sorted(glob.glob("?.npy")))
    npy_files.extend(sorted(glob.glob("??.npy")))
    npy_files.extend(sorted(glob.glob("???.npy")))
    npy_files.extend(sorted(glob.glob("????.npy")))
    npy_files.extend(sorted(glob.glob("?????.npy")))
    bar: ProgressBar = progressbar.ProgressBar(maxval=len(npy_files))
    bar.start()
    for npy_file in npy_files:
        wav_file = f"wg-{os.path.splitext(npy_file)[0]}.wav"
        nd_array = numpy.load(npy_file)
        spectrogram: Tensor = torch.from_numpy(nd_array).float()
        # spectrogram = 20 * torch.log10(torch.clamp(spectrogram, min=1e-5)) - 20
        spectrogram = torch.clamp((spectrogram + 100) / 100, 0.0, 1.0)
        audio, sr = diffwave_predict(spectrogram, model_dir, device=torch.device("cuda"))
        torchaudio.save(wav_file, audio.cpu(), sample_rate=sr)
        bar.update(bar.currval+1)
    bar.finish()


if __name__ == "__main__":
    main()
