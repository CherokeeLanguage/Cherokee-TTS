#!/bin/bash

set -e
set -o pipefail

TEXT="ᎼᏏ ᎢᎬᏱᏱ ᎤᏬᏪᎳᏅᎯ. ᎠᏯᏙᎸᎢ ᏌᏉ. ᏗᏓᎴᏂᏍᎬᎢ ᎤᏁᎳᏅᎯ ᏚᏬᏢᏁ ᎦᎸᎶᎢ ᎠᎴ ᎡᎶᎯ.";

./tts.sh --checkpoint cherokee5c_loss-245-0.119 --text "$TEXT" --voice 10-chr --griffin_lim --wav 01.wav
./tts.sh --checkpoint cherokee5c_loss-245-0.119 --text "$TEXT" --voice 04-chr --griffin_lim --wav 02.wav
./tts.sh --checkpoint cherokee5c_loss-245-0.119 --text "$TEXT" --voice 10-chr --wav 03.wav
