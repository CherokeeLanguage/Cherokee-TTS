#!/usr/bin/env python3

import torch
import soundfile as sf
import numpy as np

vocoder = torch.hub.load("seungwonpark/melgan", "melgan")
vocoder.eval()

npy = np.load("npy/1.npy")
mel = torch.tensor(npy)

print(mel.shape)

if len(mel.shape)==2:
    mel = mel.unsqueeze(0)
    
with torch.no_grad():
    audio = vocoder.inference(mel)
    audio = audio.cpu().detach().numpy()

sf.write("npy-1.wav", audio, 22050)
    