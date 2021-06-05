#!/bin/bash

set -e
set -o pipefail

# "cno-spk_0" "cno-spk_1" "cno-spk_2" "cno-spk_3"

CP="2a-2021-05-01-epoch_300-loss_0.0740"

TEXT="na wě:sa à:nő:sda. nà:sgi ga:ji:ya:du:líha"
TEXT="nà:sgi à:nő:sda gi:hli áhani gè:sv̌:gi"

./tts.sh --gpu --checkpoint $CP --text "$TEXT" --voice 299-en-f --wav 299-en-f.wav
./tts.sh --gpu --checkpoint $CP --text "$TEXT" --voice 360-en-m --wav 360-en-m.wav
#./tts.sh --gpu --checkpoint $CP --text "$TEXT" --voice cno-spk_0 --wav cno-spk_0.wav
#./tts.sh --gpu --checkpoint $CP --text "$TEXT" --voice cno-spk_1 --wav cno-spk_1.wav
#./tts.sh --gpu --checkpoint $CP --text "$TEXT" --voice cno-spk_2 --wav cno-spk_2.wav
#./tts.sh --gpu --checkpoint $CP --text "$TEXT" --voice cno-spk_3 --wav cno-spk_3.wav
#./tts.sh --gpu --checkpoint $CP --text "$TEXT" --voice 01-chr --wav 01-chr.wav
