#!/usr/bin/env python3
import os
import sys
import string

os.chdir(os.path.dirname(sys.argv[0]))

c1: string = "cdghjklmnstwy "
c2: string = "cdghjklmnst"

v1: string = "aeiouv"
v2: string = "āēīōūv"

counter: int = 0
text: string = ""

rawSyllableCount:int = 0

syllableCount:int = 0

# Open vowel syllables with level tone SHORT NASAL vowels that are marked with an macron.
for a in c1:
    if a == "c":
        a = "ch"
    if a == " ":
        a = ""
    for b in v2:
        rawSyllableCount += 1
        if rawSyllableCount % 4 == 0:
            continue
        if rawSyllableCount % 7 == 0:
            continue
        counter += 1
        syllableCount += 1
        if b == "v":
            b = b + "\u0304"
        if (text != ""):
            text += " "
        text += a + b + "."
        if counter % 7 == 0:
            print(text)
            text = ""

if text != "":
    print(text)
    
# Enclosed syllables with level tone LONG vowels that are plain.
text = ""
for a in c1:
    if a == "c":
        a = "ch"
    if a == " ":
        a = ""
    for b in v1:
        for c in c2:
            rawSyllableCount += 1
            if rawSyllableCount % 3 == 0:
                continue
            if rawSyllableCount % 7 == 0:
                continue
            if rawSyllableCount % 11 == 0:
                continue
            syllableCount += 1
            counter += 1
            if c == "c":
                c = "ch"
            if (text != ""):
                text += " "
            text += a + b + ":" + c + "."
            if counter % 7 == 0:
                print(text)
                text = ""
            
if text != "":
    print(text)

print("Total syllables for recording", syllableCount)

sys.exit(0)
            
