#!/usr/bin/env -S conda run -n Cherokee-TTS python

import subprocess
import argparse
import os
import sys

if __name__ == "__main__":
    
    bindir:str = os.path.dirname(__file__)
    workdir:str = os.getcwd()

    print(f"Workdir: {workdir}")
    
    parser = argparse.ArgumentParser(description="Conveniance wrapper for synthesize.py and wavegen.py")
    parser.add_argument("--checkpoint", type=str, required=True, help="Model checkpoint.")
    parser.add_argument("--griffin_lim", action="store_true", help="Perform Griffin Lim vocoding instead of WaveGen vocoding.")
    parser.add_argument("--lang", type=str, default="chr", help="Language to synthesize in.")
    parser.add_argument("--voice", type=str, default="cno-spk_1", help="Voice to synthesize with.")
    parser.add_argument("--wav", type=str, default="tts.wav", help="Destination wav file. Should be an absolute path!")
    parser.add_argument("--text", type=str, default="O:síyo. Tò:hi̋:ju?", help="Text to synthesize.")
    parser.add_argument("--gpu", action="store_true", help="Use GPU to synthesize.")
    args = parser.parse_args()

    synrun:list=["python", bindir + "/../synthesize.py"]
    synrun.extend(["--checkpoint", bindir + "/../checkpoints/" + args.checkpoint])
    if not args.griffin_lim:
        synrun.extend(["--save_spec", "--ignore_wav"])

    text:str=f"tmp|{args.text}|{args.voice}|{args.lang}"
    result = subprocess.run(synrun, input=text, text=True, check=True)

    if not args.griffin_lim:
        sysrun = [bindir+"/wavernnx.py"]
        if args.gpu:
            sysrun.extend(["--gpu"])
        subprocess.run(sysrun, check=True)
        os.remove("tmp.npy")
    
    os.replace("tmp.wav", args.wav)
