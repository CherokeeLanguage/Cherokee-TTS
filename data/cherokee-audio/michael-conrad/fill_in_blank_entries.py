#!/usr/bin/env python3
import re

lines:list=[]
with open("michael-conrad-annotated.txt", "r") as f:
    for line in f:
        line = line.strip()
        if line[-1]=="|":
            parts=line.split("|")
            if len(parts) != 3:
                continue
            text = parts[1]
            text = re.sub("^.*?/[0-9]+-(.*?).mp3", "\\1", text)
            text = text.replace("-", " ").strip()
            for v in "aeiouvAEIOUV":
                text = text.replace(v, v+"\u030a")
            if text[-1] == "\u030a":
                text = text[:-1]
            line += text
        lines.append(line)
        
with open("michael-conrad.txt", "w") as f:
    for line in lines:
        print(line, file=f)