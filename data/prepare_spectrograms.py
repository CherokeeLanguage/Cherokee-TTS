import sys
import os
import unicodedata as ud

from preprocess import *

sys.path.insert(0, "../")

from utils import audio
from params.params import Params as hp
import numpy as np

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str, default="datasets/1a",
                        help="Directory for Training Data (train.txt, val.txt) and Spectrogram Storage.")
    parser.add_argument("--sample_rate", type=int, default=22050, help="Sample rate.")
    parser.add_argument("--num_fft", type=int, default=1102, help="Number of FFT frequencies.")
    parser.add_argument("--num_mels", type=int, default=80, help="Number of mel bins.")
    parser.add_argument("--stft_window_ms", type=float, default=50, help="STFT window size.")
    parser.add_argument("--stft_shift_ms", type=float, default=12.5, help="STFT window shift.")
    parser.add_argument("--no_preemphasis", action='store_false', help="Do not use preemphasis.")
    parser.add_argument("--preemphasis", type=float, default=0.97, help="Strength of preemphasis.")

    args = parser.parse_args()

    hp.sample_rate = args.sample_rate
    hp.num_fft = args.num_fft

    files_to_solve = [(args.directory, "train.txt"), (args.directory, "val.txt"), ]

    spectrogram_dirs = [os.path.join(args.directory, 'mel_spectrograms')]

    for x in spectrogram_dirs:
        if not os.path.exists(x): os.makedirs(x)

    metadata = []
    for d, fs in files_to_solve:
        with open(os.path.join(d, fs), 'r', encoding='utf-8') as f:
            metadata.append((d, fs, [line.rstrip().split('|') for line in f]))

    specId: int = 0
    print(f'Please wait, this may take a very long time.')
    for d, fs, m in metadata:
        print(f'Creating spectrograms for: {fs}')

        with open(os.path.join(d, fs + "-tmp"), 'w', encoding='utf-8') as f:
            for i in m:
                idx, speaker, lang, wav, _, _, raw_text, phonemes = i
                specId += 1
                spec_name = f"{lang}_{speaker}-{specId:06d}.npy"
                audio_path = os.path.join(d, wav)
                audio_data = audio.load(audio_path)

                mel_path_partial = os.path.join("mel_spectrograms", spec_name)
                mel_path = os.path.join(d, mel_path_partial)
                if not os.path.exists(mel_path):
                    np.save(mel_path, audio.spectrogram(audio_data, True))

                raw_text = ud.normalize("NFC", raw_text)
                phonemes = ud.normalize("NFC", phonemes)
                print(f'{idx}|{speaker}|{lang}|{wav}|{mel_path_partial}||{raw_text}|{phonemes}',
                      file=f)

                if specId % 1000 == 0:
                    print(f'{idx}|{speaker}|{lang}|{wav}|{mel_path_partial}||{raw_text}|{phonemes}')

    for d, fs in files_to_solve:
        tmp = os.path.join(d, fs + "-tmp")
        dst = os.path.join(d, fs)
        bkup = os.path.join(d, fs + "-bkup")

        if os.path.exists(bkup):
            os.remove(bkup)

        os.rename(dst, bkup)
        os.rename(tmp, dst)

    sys.exit()


if __name__ == "__main__":
    main()
