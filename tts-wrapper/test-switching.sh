#!/bin/bash

set -e
set -o pipefail

CP="generated_switching.pyt"
V="00-de"

L="de"
TEXT="Ein bestimmtes Lebensmittel aus dem Kühlschrank scheint euch alle besonders zu interessieren."
./tts.sh --lang "$L" --checkpoint $CP --text "$TEXT" --voice $V --wav ${V}_${L}.wav

L="fr"
TEXT="trois cent vingt allée des Névons, quatre-vingt-quatre, huit cents à L'Isle-sur-la-Sorgue"
./tts.sh --lang "$L" --checkpoint $CP --text "$TEXT" --voice $V --wav ${V}_${L}.wav

L="nl"
TEXT="Het is een typisch kenmerk van die ziekte volgens mijn dokter."
./tts.sh --lang "$L" --checkpoint $CP --text "$TEXT" --voice $V --wav ${V}_${L}.wav

L="ru"
TEXT="Третье: ключом к решению проблем всегда является профилактика."
./tts.sh --lang "$L" --checkpoint $CP --text "$TEXT" --voice $V --wav ${V}_${L}.wav

