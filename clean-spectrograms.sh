#!/bin/bash

cd "$(dirname "$0")" || exit 1

find ./data -name lin_spectrograms | while read -r d; do
  echo "$d"
  rm -r "$d"
done

find ./data -name mel_spectrograms | while read -r d; do
  echo "$d"
  rm -r "$d"
done

exit 0
