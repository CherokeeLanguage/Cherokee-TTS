#!/bin/bash

set -e
set -o pipefail

# "cno-spk_0" "cno-spk_1" "cno-spk_2" "cno-spk_3"

CP="cherokee5c_loss-110-0.104"

TEXT="na wě:sa à:nő:sda. nà:sgi ga:ji:ya:du:líha"
TEXT="nà:sgi à:nő:sda gi:hli áhani gè:sv̌:gi"

./tts.sh --checkpoint $CP --text "$TEXT" --voice 10-chr --wav 10-chr.wav
./tts.sh --checkpoint $CP --text "$TEXT" --voice cno-spk_0 --wav cno-spk_0.wav
./tts.sh --checkpoint $CP --text "$TEXT" --voice cno-spk_1 --wav cno-spk_1.wav
./tts.sh --checkpoint $CP --text "$TEXT" --voice cno-spk_2 --wav cno-spk_2.wav
./tts.sh --checkpoint $CP --text "$TEXT" --voice cno-spk_3 --wav cno-spk_3.wav
./tts.sh --checkpoint $CP --text "$TEXT" --voice 01-chr --wav 01-chr.wav
./tts.sh --checkpoint $CP --text "$TEXT" --voice 04-chr --wav 04-chr.wav

