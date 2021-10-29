import shutil
import unicodedata as ud

import argparse
import numpy as np
import os
import progressbar
import sys
from numpy import array
from pydub import AudioSegment
from pydub import effects
from pydub.silence import detect_leading_silence

from params.params import Params as params
from utils import audio


def trim_silence(audio_segment: AudioSegment) -> AudioSegment:
    silence_threshold: float = -40

    def trim_leading_silence(tmp_audio: AudioSegment):
        return tmp_audio[detect_leading_silence(tmp_audio, silence_threshold=silence_threshold):]

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
    parser.add_argument("--dataset", type=str, default="1a",
                        help="Params dataset for Training Data.")
    parser.add_argument("--pad", type=bool, default=True, help="Pad audio with silence.")

    args = parser.parse_args()
    params.load(f"../params/{args.dataset}.json")

    dataset_path: str = os.path.join("datasets", args.dataset)
    files_to_solve = [(dataset_path, "train.txt"), (dataset_path, "val.txt"), ]

    mel_path: str = os.path.join(dataset_path, 'mel_spectrograms')
    os.makedirs(mel_path, exist_ok=True)

    mp3_path: str = os.path.join(dataset_path, "reference-audio")
    shutil.rmtree(mp3_path, ignore_errors=True)
    os.mkdir(mp3_path)

    metadata = []
    for d, fs in files_to_solve:
        with open(os.path.join(d, fs), 'r', encoding='utf-8') as f:
            metadata.append((d, fs, [line.rstrip().split('|') for line in f]))

    spec_id: int = 0
    print(f'Please wait, this may take a very long time.')
    for d, fs, m in metadata:
        print(f'Creating spectrograms for: {fs}')
        bar: progressbar.ProgressBar = progressbar.ProgressBar(maxval=len(m))
        bar.start()
        with open(os.path.join(d, fs + "-tmp"), 'w', encoding='utf-8') as f:
            for i in m:
                idx, speaker, lang, wav, _, _, raw_text, phonemes = i
                spec_id += 1
                spec_name = f"{lang}_{speaker}-{spec_id:06d}.npy"
                audio_path = os.path.join(d, wav)

                py_audio: AudioSegment = AudioSegment.from_file(audio_path)
                py_audio = py_audio.set_channels(1).set_frame_rate(params.sample_rate)
                py_audio = effects.normalize(py_audio)
                py_audio = trim_silence(py_audio)

                # pydub.silence.detect_silence(py_audio, silence_thresh=-40, seek_step=10)
                # TODO: scan for long silence gaps and either reject the sample or reduce the length of the silence gaps

                if args.pad:
                    # Add 100 ms of silence at the beginning, and 150 ms at the end.
                    py_audio = AudioSegment.silent(100) + py_audio + AudioSegment.silent(150)

                # Output altered audio (compressed) for manual review
                mp3_name = f"{lang}_{speaker}-{spec_id:06d}.mp3"
                ref_audio_mp3: str = os.path.join(mp3_path, mp3_name)
                if not os.path.exists(ref_audio_mp3):
                    py_audio.export(ref_audio_mp3, format="mp3", parameters=["-qscale:a", "3"])

                py_audio_samples: array = np.array(py_audio.get_array_of_samples()).astype(np.float32)
                py_audio_samples = py_audio_samples / (1 << 8 * 2 - 1)
                mel_path_partial = os.path.join("mel_spectrograms", spec_name)
                mel_path = os.path.join(dataset_path, mel_path_partial)
                if not os.path.exists(mel_path):
                    np.save(mel_path, audio.spectrogram(py_audio_samples, True))

                raw_text = ud.normalize("NFC", raw_text)
                phonemes = ud.normalize("NFC", phonemes)

                print(f'{idx}|{speaker}|{lang}|{wav}|{mel_path_partial}||{raw_text}|{phonemes}', file=f)
                bar.update(bar.currval + 1)

        bar.finish()

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
