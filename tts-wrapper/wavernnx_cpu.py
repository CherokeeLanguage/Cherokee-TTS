import os
import sys
import numpy as np
import soundfile as sf
import torch
import librosa

cwd:str = os.getcwd()

bindir:str = os.getcwd()
if (sys.argv[0].strip()!=""):
    bindir:str = os.path.dirname(sys.argv[0])
        
CHECKPOINTS_FOLDER = bindir + "/_checkpoints"
GIT_FOLDER = bindir + "/../../../git"

if not os.path.isdir(CHECKPOINTS_FOLDER):
    os.mkdir(CHECKPOINTS_FOLDER)

wavernn_chpt = "wavernn_weight.pyt"
WAVERNN_FOLDER = GIT_FOLDER + "/WaveRNN"
WAVERNN_WEIGHTS = CHECKPOINTS_FOLDER + "/" + wavernn_chpt

if not os.path.exists(CHECKPOINTS_FOLDER + "/" + wavernn_chpt):
    os.chdir(CHECKPOINTS_FOLDER)
    os.system("curl -O -L 'https://github.com/Tomiinek/Multilingual_Text_to_Speech/releases/download/v1.0/" +wavernn_chpt+"'")

if "utils" in sys.modules:
    del sys.modules["utils"]

sys.path.append(WAVERNN_FOLDER)

from gen_wavernn import generate
from utils import hparams as hp
from models.fatchord_version import WaveRNN

hp.configure(WAVERNN_FOLDER+'/hparams.py')
model = WaveRNN(rnn_dims=hp.voc_rnn_dims, fc_dims=hp.voc_fc_dims, bits=hp.bits, pad=hp.voc_pad,
                upsample_factors=hp.voc_upsample_factors, feat_dims=hp.num_mels,
                compute_dims=hp.voc_compute_dims, res_out_dims=hp.voc_res_out_dims, res_blocks=hp.voc_res_blocks,
                hop_length=hp.hop_length, sample_rate=hp.sample_rate, mode="RAW").to('cpu')
#mode=hp.voc_mode
model.load(CHECKPOINTS_FOLDER + "/" + wavernn_chpt)

# batched = hp.voc_gen_batched, target=hp.voc_target, overlap=hp.voc_overlap

waveform = generate(model, np.load(cwd+"/tmp.npy"), batched=True, target=11025, overlap=int(11025/4))
sf.write(cwd+"/tmp.wav", waveform, hp.sample_rate)
