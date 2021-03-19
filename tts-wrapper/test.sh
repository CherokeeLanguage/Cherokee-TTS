#!/bin/bash

set -e
set -o pipefail

CP="cherokee5c_loss-110-0.104"

TEXT="ᎼᏏ ᎢᎬᏱᏱ ᎤᏬᏪᎳᏅᎯ. ᎠᏯᏙᎸᎢ ᏌᏉ. ᏗᏓᎴᏂᏍᎬᎢ ᎤᏁᎳᏅᎯ ᏚᏬᏢᏁ ᎦᎸᎶᎢ ᎠᎴ ᎡᎶᎯ.";

./tts.sh --checkpoint $CP --text "$TEXT" --voice 10-chr --griffin_lim --wav 10-chr_syl_gl.wav
./tts.sh --checkpoint $CP --text "$TEXT" --voice 04-chr --griffin_lim --wav 04-chr_syl_gl.wav
./tts.sh --checkpoint $CP --text "$TEXT" --voice 10-chr --wav 10-chr_syl.wav
