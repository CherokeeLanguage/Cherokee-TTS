#!/usr/bin/env -S conda run -n Cherokee-TTS python
import shutil
import subprocess
import argparse
import os
import sys


def test():
    bindir: str

    if sys.argv[0] and os.path.dirname(sys.argv[0]):
        bindir = os.path.dirname(sys.argv[0])
    else:
        bindir = os.path.dirname(__file__)

    script: str = f"""
            PS1='$'
            . ~/.bashrc
            conda deactivate
            conda activate Cherokee-TTS
            python "{bindir}/wavernnx.py"            
            exit 0
            """
    subprocess.run(script, shell=True, executable="/bin/bash", check=True)


def main():
    bindir: str

    if sys.argv[0] and os.path.dirname(sys.argv[0]):
        bindir = os.path.dirname(sys.argv[0])
    else:
        bindir = os.path.dirname(__file__)

    workdir: str = os.getcwd()

    print(f"Workdir: {workdir}")

    parser = argparse.ArgumentParser(description="Conveniance wrapper for synthesize.py and UniversalVocoder")
    parser.add_argument("--checkpoint", type=str, required=True, help="Model checkpoint.")
    parser.add_argument("--griffin_lim", action="store_true",
                        help="Perform Griffin Lim vocoding instead of using UniversalVocoding package.")
    parser.add_argument("--lang", type=str, default="chr", help="Language to synthesize in.")
    parser.add_argument("--voice", type=str, default="cno-spk_1", help="Voice to synthesize with.")
    parser.add_argument("--wav", type=str, default="tts.wav", help="Destination wav file. Should be an absolute path!")
    parser.add_argument("--text", type=str, default="O:síyo. Tò:hi̋:ju?", help="Text to synthesize.")
    parser.add_argument("--gpu", action="store_true", help="Use GPU to synthesize.")
    args = parser.parse_args()

    synrun: list = ["python", bindir + "/../synthesize.py"]
    synrun.extend(["--checkpoint", bindir + "/../checkpoints/" + args.checkpoint])
    if not args.griffin_lim:
        synrun.extend(["--save_spec", "--ignore_wav"])
    if not args.gpu:
        synrun.extend(["--cpu"])

    text: str = f"tmp|{args.text}|{args.voice}|{args.lang}"
    result = subprocess.run(synrun, input=text, text=True, check=True)

    if not args.griffin_lim:
        gpu_option: str = "\"--gpu\"" if args.gpu else ""
        script: str = f"""
            PS1='$'
            . ~/.bashrc
            conda deactivate
            conda activate Cherokee-TTS
            python "{bindir}/wavernnx.py" {gpu_option}
            exit 0
        """
        subprocess.run(script, shell=True, executable="/bin/bash", check=True)
        os.remove(os.path.join(workdir, "tmp.npy"))

    shutil.move(os.path.join(workdir, "tmp.wav"), args.wav)


if __name__ == "__main__":
    main()
