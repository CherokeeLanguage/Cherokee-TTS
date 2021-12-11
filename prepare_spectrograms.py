import subprocess

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

from params.params import Params
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
    parser.add_argument("--dataset", type=str, default="1a",  #
                        help="Params dataset for Training Data.")

    args = parser.parse_args()
    Params.load(f"../params/{args.dataset}.json")
    audio.hp = Params
    hop_frames: int = audio.ms_to_frames(audio.hp.stft_shift_ms)
    win_frames: int = audio.ms_to_frames(audio.hp.stft_window_ms)
    print(f"mel parameters: hop = {hop_frames:,}, win = {win_frames:,}")
    dataset_path: str = os.path.join("datasets", args.dataset)

    # as this code *alters* the train and val files, always regenerate them first!
    _: List[str] = ["python", os.path.join(dataset_path, "create_training_files.py")]
    subprocess.run(_, check=True, bufsize=0)

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

                if lang not in Params.languages:
                    continue

                raw_text = ud.normalize("NFC", raw_text)
                phonemes = ud.normalize("NFC", phonemes)

                spec_id += 1
                spec_name = f"{lang}_{speaker}-{spec_id:06d}.npy"

                mel_path_partial = os.path.join("mel_spectrograms", spec_name)
                mel_path = os.path.join(dataset_path, mel_path_partial)

                entry: str = f'{idx}|{speaker}|{lang}|{wav}|{mel_path_partial}||{raw_text}|{phonemes}'

                audio_path = os.path.join(d, wav)

                py_audio: AudioSegment = AudioSegment.from_file(audio_path)
                py_audio = py_audio.set_channels(1).set_frame_rate(Params.sample_rate)
                py_audio = effects.normalize(py_audio)
                py_audio = trim_silence(py_audio)

                # Output altered audio (compressed) for manual review
                mp3_name = f"{lang}_{speaker}-{spec_id:06d}.mp3"
                ref_audio_mp3: str = os.path.join(mp3_path, mp3_name)

                if Params.fix_silence:
                    fix_silence: int = Params.fix_silence_len
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

                if Params.skip_silence:
                    max_silence: int = Params.max_silence_len
                    if silence.detect_silence(py_audio,  #
                                              min_silence_len=max_silence,  #
                                              silence_thresh=-50):
                        with open(file_bad_entries, "a") as w:
                            print(entry, file=w)
                        bad_audio_mp3: str = os.path.join(mp3_bad_path, f"bad-{mp3_name}")
                        py_audio.export(bad_audio_mp3, format="mp3", parameters=["-qscale:a", "3"])
                        bad_silence_count += 1
                        continue

                if len(py_audio) < Params.audio_min_length:
                    skipped_too_short.append(entry)
                    bad_audio_mp3: str = os.path.join(mp3_bad_path, f"too-short-{mp3_name}")
                    py_audio.export(bad_audio_mp3, format="mp3", parameters=["-qscale:a", "3"])
                    continue

                if len(py_audio) > Params.audio_max_length:
                    skipped_too_long.append(entry)
                    bad_audio_mp3: str = os.path.join(mp3_bad_path, f"too-long-{mp3_name}")
                    py_audio.export(bad_audio_mp3, format="mp3", parameters=["-qscale:a", "3"])
                    continue

                if Params.lead_in_silence > 0:
                    # Add lead_in_silence ms of silence at the beginning
                    py_audio = AudioSegment.silent(Params.lead_in_silence) + py_audio

                if Params.lead_out_silence > 0:
                    # Add lead_out_silence ms of silence at the end
                    py_audio = py_audio + AudioSegment.silent(Params.lead_out_silence)

                if not os.path.exists(ref_audio_mp3):
                    py_audio.export(ref_audio_mp3, format="mp3", parameters=["-qscale:a", "3"])

                py_audio_samples: array = np.array(py_audio.get_array_of_samples()).astype(np.float32)
                py_audio_samples = py_audio_samples / (1 << 8 * 2 - 1)
                if not os.path.exists(mel_path):
                    np.save(mel_path, audio.spectrogram(py_audio_samples, True))

                print(entry, file=f)
                bar.update(bar.currval + 1)

        print(f"Records skipped (>{Params.audio_max_length / 1000:.02f}): {len(skipped_too_long):,}")
        with open(os.path.join(d, "too-long-" + fs), "w") as w:
            for entry in skipped_too_long:
                print(entry, file=w)

        print(f"Records skipped (<{Params.audio_min_length / 1000:.02f}): {len(skipped_too_short):,}")
        with open(os.path.join(d, "too-short-" + fs), "w") as w:
            for entry in skipped_too_short:
                print(entry, file=w)

        bar.finish()

    if bad_silence_count:
        print(f"Records skipped because of excessive silence: {bad_silence_count:,}")
    if fix_silence_count:
        print(f"Records altered because of excessive silence: {fix_silence_count:,}")

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
