#!/bin/bash

cd "$(dirname "$0")" || exit 1

find . -name lin_spectograms | while read -r d; do
  echo "$d"
  rm -r "$d"
done

find . -name mel_spectograms | while read -r d; do
  echo "$d"
  rm -r "$d"
done
