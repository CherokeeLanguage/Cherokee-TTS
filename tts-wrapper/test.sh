#!/bin/bash

set -e
set -o pipefail

CP="cherokee5c_loss-305-0.119"

TEXT="ᎼᏏ ᎢᎬᏱᏱ ᎤᏬᏪᎳᏅᎯ. ᎠᏯᏙᎸᎢ ᏌᏉ. ᏗᏓᎴᏂᏍᎬᎢ ᎤᏁᎳᏅᎯ ᏚᏬᏢᏁ ᎦᎸᎶᎢ ᎠᎴ ᎡᎶᎯ.";

./tts.sh --checkpoint $CP --text "$TEXT" --voice 10-chr --griffin_lim --wav 01.wav
./tts.sh --checkpoint $CP --text "$TEXT" --voice 04-chr --griffin_lim --wav 02.wav
./tts.sh --checkpoint $CP --text "$TEXT" --voice 10-chr --wav 03.wav
