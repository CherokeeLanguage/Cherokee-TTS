#!/usr/bin/env python3
import os
import sys
import string
import unicodedata as ud
import random
import re
import csv

from chrutils.chrutils import ced2mco
from chrutils.chrutils import ascii_ced2mco
from cairosvg.shapes import line
from tabulate import Line

os.chdir(os.path.dirname(sys.argv[0]))

CED:str="ced.csv"
CEDMCO:str="ced-mco.txt"

ASCII_CED_TONES=["entrytone","nounadjpluraltone","vfirstprestone","vsecondimpertone","vthirdinftone","vthirdpasttone","vthirdprestone"]

ced2mco = []

CGRAVEACCENT="\u0300"
CACUTEACCENT="\u0301"
CCARON="\u0302"
CMACRON="\u0304"
CDOUBLEACUTE="\u030b"
CCIRCUMFLEX="\u030c"
CMACRONBELOW="\u0331"

#Build guessing pronunciation lookup for transliterated text
with open(CED, newline='') as csvfile:
    rows = csv.DictReader(csvfile)
    for row in rows:
        id:str=row["id"]
        if not re.match("\d+", id):
            continue
        line:str=str(id)+"|"
        for key in ASCII_CED_TONES:
            value:str = row[key]
            if (value == ""):
                line+="|"
                continue
            value=ud.normalize("NFC", ascii_ced2mco(value)).lower().capitalize()
            if value[-1] not in ".?!":
                value += "."
            line += value + "|"
        
        definition:str=row["definitiond"]
        line += definition
        ced2mco.append(line)

with  open(CEDMCO, "w") as f:
    for line in ced2mco:
        f.write(line)
        f.write("\n")
        
sys.exit()

