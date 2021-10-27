import unicodedata as ud

import argparse
import numpy as np
import os
import sys
from numpy import array
from pydub import AudioSegment
from pydub import effects
from pydub.silence import detect_leading_silence

from params.params import Params as params
from utils import audio


def trim_silence(audio_segment: AudioSegment) -> AudioSegment:

    def trim_leading_silence(tmp_audio: AudioSegment):
        return tmp_audio[detect_leading_silence(tmp_audio):]

    def trim_trailing_silence(tmp_audio: AudioSegment):
        tmp_reversed: AudioSegment = tmp_audio.reverse()
        return tmp_reversed[detect_leading_silence(tmp_reversed):].reverse()

    return trim_trailing_silence(trim_leading_silence(audio_segment))


def main():
    argv0: str = sys.argv[0]
    if argv0:
        workdir: str = os.path.dirname(argv0)
        if workdir:
            os.chdir(workdir)
    os.chdir("data")

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
    parser.add_argument("--pad", type=bool, default=True, help="Pad audio with silence.")

    args = parser.parse_args()

    params.sample_rate = args.sample_rate
    params.num_fft = args.num_fft

    files_to_solve = [(args.directory, "train.txt"), (args.directory, "val.txt"), ]

    spectrogram_dirs = [os.path.join(args.directory, 'mel_spectrograms')]

    for x in spectrogram_dirs:
        if not os.path.exists(x):
            os.makedirs(x)

    metadata = []
    for d, fs in files_to_solve:
        with open(os.path.join(d, fs), 'r', encoding='utf-8') as f:
            metadata.append((d, fs, [line.rstrip().split('|') for line in f]))

    spec_id: int = 0
    print(f'Please wait, this may take a very long time.')
    for d, fs, m in metadata:
        print(f'Creating spectrograms for: {fs}')

        with open(os.path.join(d, fs + "-tmp"), 'w', encoding='utf-8') as f:
            for i in m:
                idx, speaker, lang, wav, _, _, raw_text, phonemes = i
                spec_id += 1
                spec_name = f"{lang}_{speaker}-{spec_id:06d}.npy"
                audio_path = os.path.join(d, wav)

                py_audio: AudioSegment = AudioSegment.from_file(audio_path)
                py_audio = py_audio.set_channels(1).set_frame_rate(params.sample_rate)
                py_audio = trim_silence(py_audio)

                if args.pad:
                    # Add 100 ms of silence at the beginning, and 150 ms at the end.
                    py_audio = AudioSegment.silent(100) + py_audio + AudioSegment.silent(150)

                py_audio = effects.normalize(py_audio)
                py_audio_samples: array = np.array(py_audio.get_array_of_samples()).astype(np.float32)
                py_audio_samples = py_audio_samples / (1 << 8 * 2 - 1)

                mel_path_partial = os.path.join("mel_spectrograms", spec_name)
                mel_path = os.path.join(d, mel_path_partial)
                if not os.path.exists(mel_path):
                    np.save(mel_path, audio.spectrogram(py_audio_samples, True))

                raw_text = ud.normalize("NFC", raw_text)
                phonemes = ud.normalize("NFC", phonemes)
                print(f'{idx}|{speaker}|{lang}|{wav}|{mel_path_partial}||{raw_text}|{phonemes}', file=f)

                if spec_id % 1000 == 0:
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
