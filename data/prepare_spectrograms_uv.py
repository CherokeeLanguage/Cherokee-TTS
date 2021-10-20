import unicodedata as ud
import os
import sys
import librosa

import numpy as np
from numpy import array
from pydub import AudioSegment
from pydub import effects
from preprocess import *

sys.path.insert(0, "../")

from params.params import Params as hp


def uv_mel_spectrogram(
        wav,  #
        sr=16000,  #
        hop_length=200,  #
        win_length=800,  #
        n_fft=2048,  #
        n_mels=128,  #
        preemph=0.97,  #
        top_db=80,  #
        ref_db=20,  #
        ) -> np.ndarray:
    mel: np.ndarray = librosa.feature.melspectrogram(  #
        librosa.effects.preemphasis(wav, coef=preemph),  #
        sr=sr,  #
        hop_length=hop_length,  #
        win_length=win_length,  #
        n_fft=n_fft,  #
        n_mels=n_mels,  #
        norm=1,  #
        power=1,  #
    )
    log_mel = librosa.amplitude_to_db(mel, top_db=None) - ref_db
    log_mel = np.maximum(log_mel, -top_db)
    return log_mel / top_db


def ms_to_frames(ms: int) -> int:
    """Convert milliseconds into number of frames.
    :rtype: int
    """
    return int(hp.sample_rate * ms / 1000)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="2a",
                        help="Dataset Directory for Training Data (train.txt, val.txt) and Spectrogram Storage.")
    parser.add_argument("--pad", type=bool, default=True,
                        help="Pad audio with lead-in (250ms) and lead-out (500ms) silence.")

    args = parser.parse_args()

    dataset: str = args.dataset
    hp.load(f"../params/{dataset}.json")

    if not hp.universal_vocoding:
        raise RuntimeError("Universal Vocoding is False")

    dataset_path: str = os.path.join("datasets", dataset)
    files_to_solve = [(dataset_path, "train.txt"), (dataset_path, "val.txt"), ]

    spectrogram_dirs = [os.path.join(dataset_path, 'mel_spectrograms')]

    wf: int = ms_to_frames(hp.stft_window_ms)
    hf: int = ms_to_frames(hp.stft_shift_ms)

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
                audio_path: str = os.path.join(d, wav)

                py_audio: AudioSegment = AudioSegment.from_file(audio_path)
                py_audio = py_audio.set_channels(1).set_frame_rate(hp.sample_rate)
                if args.pad:
                    py_audio = AudioSegment.silent(250) + py_audio + AudioSegment.silent(500)
                py_audio = effects.normalize(py_audio)
                py_audio_samples: array = np.array(py_audio.get_array_of_samples()).astype(np.float32)
                py_audio_samples = py_audio_samples / (1 << 8*2 - 1)

                mel_path_partial = os.path.join("mel_spectrograms", spec_name)
                mel_path = os.path.join(d, mel_path_partial)
                if not os.path.exists(mel_path):
                    mel = uv_mel_spectrogram(py_audio_samples,
                                             sr=hp.sample_rate,
                                             hop_length=hf,
                                             win_length=wf,
                                             n_fft=hp.num_fft,
                                             n_mels=hp.num_mels)
                    np.save(mel_path, mel)

                raw_text = ud.normalize("NFC", raw_text)
                phonemes = ud.normalize("NFC", phonemes)
                print(f'{idx}|{speaker}|{lang}|{wav}|{mel_path_partial}||{raw_text}|{phonemes}',
                      file=f)

                if spec_id % 500 == 0:
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
