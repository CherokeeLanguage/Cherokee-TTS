#!/usr/bin/env python3
import os
import sys
import string

os.chdir(os.path.dirname(sys.argv[0]))

v_notwanted = ["á", "é", "í", "ó", "ú", "v́", "a̋", "e̋",
               "i̋", "ő", "ű", "v̋", "à", "è", "ì", "ò",
               "ù", "v̀", "ǎ", "ě", "ǐ", "ǒ", "ǔ", "v̌",
               "â", "ê", "î", "ô", "û", "v̂"]

with open("ced-multi.txt", "r") as f:
    #
    print (f.read())
    #x = f.readline()
    #y = x.split("|")
    #print (y[1])

sys.exit()
