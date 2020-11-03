import os
import sys
import numpy as np
import soundfile as sf
import torch
import librosa

HOME = os.path.expanduser("~")
GIT_FOLDER = HOME + "/git"
CHECKPOINTS_FOLDER = GIT_FOLDER + "/_checkpoints"

if not os.path.isdir(CHECKPOINTS_FOLDER):
    os.mkdir(CHECKPOINTS_FOLDER)

TACOTRON_FOLDER = GIT_FOLDER + "/Cherokee-TTS"
CHR_FOLDER = TACOTRON_FOLDER+"/data/tests/osiyo-tohiju-then-what"

wavernn_chpt = "wavernn_weight.pyt"
WAVERNN_FOLDER = GIT_FOLDER + "/WaveRNN"
WAVERNN_WEIGHTS = CHECKPOINTS_FOLDER + "/" + wavernn_chpt

if not os.path.exists(CHECKPOINTS_FOLDER + "/" + wavernn_chpt):
    os.chdir(CHECKPOINTS_FOLDER)
    os.system("curl -O -L 'https://github.com/Tomiinek/Multilingual_Text_to_Speech/releases/download/v1.0/" +wavernn_chpt+"'")


print("Cur Dir", os.getcwd())

if "utils" in sys.modules:
    del sys.modules["utils"]

sys.path.append(WAVERNN_FOLDER)

from gen_wavernn import generate
from utils import hparams as hp
from models.fatchord_version import WaveRNN

hp.configure(WAVERNN_FOLDER+'/hparams.py')
model = WaveRNN(rnn_dims=hp.voc_rnn_dims, fc_dims=hp.voc_fc_dims, bits=hp.bits, pad=hp.voc_pad, upsample_factors=hp.voc_upsample_factors,
                feat_dims=hp.num_mels, compute_dims=hp.voc_compute_dims, res_out_dims=hp.voc_res_out_dims, res_blocks=hp.voc_res_blocks,
                hop_length=hp.hop_length, sample_rate=hp.sample_rate, mode=hp.voc_mode).to('cpu')
model.load(CHECKPOINTS_FOLDER + "/" + wavernn_chpt)

y = []

ix=1
while os.path.exists(CHR_FOLDER+"/"+str(ix)+".npy"):
    y.append(np.load(CHR_FOLDER+"/"+str(ix)+".npy"))
    ix+=1

idx=1
for s in y:
    waveform = generate(model, s, hp.voc_gen_batched,
                      hp.voc_target, hp.voc_overlap)
    sf.write("wg-"+str(idx)+".wav", waveform, hp.sample_rate)
    idx+=1
    



