from dataclasses import dataclass

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
from pydub import silence
from pydub.silence import detect_leading_silence
from typing import List
from typing import List

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


@dataclass
class SpectrogramConfig:
    pass


def main():
    argv0: str = sys.argv[0]
    if argv0:
        workdir: str = os.path.dirname(argv0)
        if workdir:
            os.chdir(workdir)
    os.chdir("data")

    max_silence: int = 500
    fix_silence: int = 400

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="1a",  #
                        help="Params dataset for Training Data.")
    parser.add_argument("--pad", type=bool, default=True,  #
                        help="Pad audio with silence.")
    parser.add_argument("--skip_silence", type=bool, default=False,  #
                        help=f"Skip audio with long periods of silence (>={max_silence}ms).")
    parser.add_argument("--fix_silence", type=bool, default=True,  #
                        help=f"Fix audio with long periods of silence (>={fix_silence}ms).")

    args = parser.parse_args()
    params.load(f"../params/{args.dataset}.json")

    dataset_path: str = os.path.join("datasets", args.dataset)
    files_to_solve = [(dataset_path, "train.txt"), (dataset_path, "val.txt"), ]

    mel_path: str = os.path.join(dataset_path, 'mel_spectrograms')
    os.makedirs(mel_path, exist_ok=True)

    mp3_path: str = os.path.join(dataset_path, "reference-audio")
    shutil.rmtree(mp3_path, ignore_errors=True)
    os.mkdir(mp3_path)

    mp3_bad_path: str = os.path.join(dataset_path, "reference-audio-bad")
    shutil.rmtree(mp3_bad_path, ignore_errors=True)
    os.mkdir(mp3_bad_path)

    mp3_fixed_path: str = os.path.join(dataset_path, "reference-audio-fixed")
    shutil.rmtree(mp3_fixed_path, ignore_errors=True)
    os.mkdir(mp3_fixed_path)

    metadata = []
    for d, fs in files_to_solve:
        with open(os.path.join(d, fs), 'r', encoding='utf-8') as f:
            metadata.append((d, fs, [line.rstrip().split('|') for line in f]))

    bad_silence_count: int = 0
    file_bad_entries: str = os.path.join(dataset_path, "entries-bad.txt")
    with open(file_bad_entries, "w"):
        pass

    fix_silence_count: int = 0
    file_fixed_entries: str = os.path.join(dataset_path, "entries-fixed.txt")
    with open(file_fixed_entries, "w"):
        pass

    skipped_too_short: List[str] = list()
    skipped_too_long: List[str] = list()
    spec_id: int = 0
    print(f'Please wait, this may take a very long time.')
    for d, fs, m in metadata:
        print(f'Creating spectrograms for: {fs}')
        bar: progressbar.ProgressBar = progressbar.ProgressBar(maxval=len(m))
        bar.start()
        with open(os.path.join(d, fs + "-tmp"), 'w', encoding='utf-8') as f:
            for i in m:
                idx, speaker, lang, wav, _, _, raw_text, phonemes = i

                raw_text = ud.normalize("NFC", raw_text)
                phonemes = ud.normalize("NFC", phonemes)

                spec_id += 1
                spec_name = f"{lang}_{speaker}-{spec_id:06d}.npy"

                mel_path_partial = os.path.join("mel_spectrograms", spec_name)
                mel_path = os.path.join(dataset_path, mel_path_partial)

                entry: str = f'{idx}|{speaker}|{lang}|{wav}|{mel_path_partial}||{raw_text}|{phonemes}'

                audio_path = os.path.join(d, wav)

                py_audio: AudioSegment = AudioSegment.from_file(audio_path)
                py_audio = py_audio.set_channels(1).set_frame_rate(params.sample_rate)
                py_audio = effects.normalize(py_audio)
                py_audio = trim_silence(py_audio)

                # pydub.silence.detect_silence(py_audio, silence_thresh=-40, seek_step=10)
                # TODO: scan for long silence gaps and either reject the sample or reduce the length of the silence gaps

                # Output altered audio (compressed) for manual review
                mp3_name = f"{lang}_{speaker}-{spec_id:06d}.mp3"
                ref_audio_mp3: str = os.path.join(mp3_path, mp3_name)

                if args.fix_silence:
                    segments = silence.split_on_silence(py_audio,  #
                                                        min_silence_len=fix_silence,  #
                                                        silence_thresh=-50,  #
                                                        keep_silence=fix_silence / 2)
                    if len(segments) > 1:
                        new_py_audio = AudioSegment.empty()
                        for segment in segments:
                            new_py_audio = new_py_audio.append(segment, crossfade=0)
                        assert len(new_py_audio), "Empty fixed audio after recombining?"

                        py_audio = new_py_audio.set_channels(1).set_frame_rate(py_audio.frame_rate)
                        with open(file_fixed_entries, "a") as w:
                            print(entry, file=w)
                        fix_audio_mp3: str = os.path.join(mp3_fixed_path, f"fix-{mp3_name}")
                        py_audio.export(fix_audio_mp3, format="mp3", parameters=["-qscale:a", "3"])
                        fix_silence_count += 1

                if args.skip_silence:
                    if silence.detect_silence(py_audio,  #
                                              min_silence_len=max_silence,  #
                                              silence_thresh=-50):
                        with open(file_bad_entries, "a") as w:
                            print(entry, file=w)
                        bad_audio_mp3: str = os.path.join(mp3_bad_path, f"bad-{mp3_name}")
                        py_audio.export(bad_audio_mp3, format="mp3", parameters=["-qscale:a", "3"])
                        bad_silence_count += 1
                        continue

                if len(py_audio) < params.audio_min_length:
                    skipped_too_short.append(entry)
                    bad_audio_mp3: str = os.path.join(mp3_bad_path, f"too-short-{mp3_name}")
                    py_audio.export(bad_audio_mp3, format="mp3", parameters=["-qscale:a", "3"])
                    continue
                    
                if len(py_audio) > params.audio_max_length:
                    skipped_too_long.append(entry)
                    bad_audio_mp3: str = os.path.join(mp3_bad_path, f"too-long-{mp3_name}")
                    py_audio.export(bad_audio_mp3, format="mp3", parameters=["-qscale:a", "3"])
                    continue

                if args.pad:
                    # Add 100 ms of silence at the beginning, and 150 ms at the end.
                    py_audio = AudioSegment.silent(100) + py_audio + AudioSegment.silent(150)

                if not os.path.exists(ref_audio_mp3):
                    py_audio.export(ref_audio_mp3, format="mp3", parameters=["-qscale:a", "3"])

                py_audio_samples: array = np.array(py_audio.get_array_of_samples()).astype(np.float32)
                py_audio_samples = py_audio_samples / (1 << 8 * 2 - 1)
                if not os.path.exists(mel_path):
                    np.save(mel_path, audio.spectrogram(py_audio_samples, True))

                print(entry, file=f)
                bar.update(bar.currval + 1)

        print(f"Records skipped (>{params.audio_max_length/1000:.02f}): {len(skipped_too_long),}")
        with open(os.path.join(d, "too-long-" + fs), "w") as w:
            for entry in skipped_too_long:
                print(entry, file=w)

        print(f"Records skipped (<{params.audio_min_length/1000:.02f}): {len(skipped_too_short),}")
        with open(os.path.join(d, "too-short-" + fs), "w") as w:
            for entry in skipped_too_short:
                print(entry, file=w)

        bar.finish()

    if bad_silence_count:
        print(f"Records skipped because of excessive silence: {bad_silence_count,}")
    if fix_silence_count:
        print(f"Records altered because of excessive silence: {fix_silence_count,}")

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
