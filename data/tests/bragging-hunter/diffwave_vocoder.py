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
from typing import List
from typing import Tuple

from diffwave.inference import predict as diffwave_predict


def cd_script_dir() -> None:
    if sys.argv[0].strip():
        dir_name: str = os.path.dirname(sys.argv[0])
        if dir_name:
            os.chdir(dir_name)


def main():
    weights_dir: str = os.path.expanduser("~/git/cherokee-diffwave/models/")
    cd_script_dir()
    model_pt = os.path.join(weights_dir, "weights.pt")
    npy_files: List[str] = list()
    npy_files.extend(sorted(glob.glob("?.npy")))
    npy_files.extend(sorted(glob.glob("??.npy")))
    npy_files.extend(sorted(glob.glob("???.npy")))
    npy_files.extend(sorted(glob.glob("????.npy")))
    npy_files.extend(sorted(glob.glob("?????.npy")))
    npy_files.extend(sorted(glob.glob("??????*.npy")))
    bar: ProgressBar = progressbar.ProgressBar(maxval=len(npy_files))
    bar.start()
    npy_wav_files: List[Tuple[str, str]] = list()
    for npy_file in npy_files:
        wav_file = f"wg-{os.path.splitext(npy_file)[0]}.wav"
        npy_wav_files.append((npy_file, wav_file))
        if os.path.isfile(wav_file):
            os.remove(wav_file)
    for npy_file, wav_file in npy_wav_files:
        nd_array = numpy.load(npy_file)
        spectrogram: Tensor = torch.from_numpy(nd_array).float()
        spectrogram = torch.clamp((spectrogram + 100) / 100, 0.0, 1.0)
        audio, sr = diffwave_predict(spectrogram, model_pt, device=torch.device("cuda"))
        torchaudio.save(wav_file, audio.cpu(), sample_rate=sr)
        bar.update(bar.currval+1)
    bar.finish()


if __name__ == "__main__":
    main()
