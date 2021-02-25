#!/usr/bin/env python3

if __name__ == "__main__":
        
    import os
    import sys
    import string
    import unicodedata as ud
    import random
    import re
    import pathlib
    import subprocess
    from shutil import rmtree
    from builtins import list
    
    output_file="thirteen-moons.txt"
    silence_threshold:float=-30.0
    silence_min_duration:int=200 #ms
    
    workdir:str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()
    
    from pydub import AudioSegment
    from pydub.effects import normalize
    
    # From https://stackoverflow.com/questions/29547218/
    # remove-silence-at-the-beginning-and-at-the-end-of-wave-files-with-pydub
    from pydub import AudioSegment
    
    def detect_sound(sound:AudioSegment, silence_threshold:float=-30.0, chunk_size:int=200)->list:
        '''
        sound is a pydub.AudioSegment
        silence_threshold in dB
        chunk_size in ms
        iterate over entire AudioSegment looking for non-silent chunks
        returns list of chunks as a list of tuples (begin, end). In milliseconds.
        returns an empty list of no sound chunks found
        '''
        sound_start:int = -1
        segments:list=list()
        
        for position in range(0, len(sound), 10): #process in 10 ms chunks
            if sound_start < 0 and sound[position:position+chunk_size].dBFS <= silence_threshold:
                continue
            if sound_start < 0:
                sound_start=position+chunk_size/2
                continue
            if sound_start >= 0 and sound[position:position+chunk_size].dBFS <= silence_threshold:
                segments.append((sound_start, position+chunk_size/2))
                sound_start=-1
                continue
            
        if sound_start >= 0:
            segments.append((int(sound_start), int(len(sound))))
            
        return segments
    
    #clean up any previous files
    rmtree("mp3", ignore_errors=True)
    os.mkdir("mp3")
    
    from os import walk
    mp3s = []
    for (dirpath, dirnames, filenames) in walk("src"):
        mp3s.extend(filenames)
        break
    mp3s.sort()
    splits:list=[]
    for mp3 in mp3s:
        if os.path.splitext(mp3)[1].lower()!=".mp3":
            continue
        mp3=os.path.splitext(mp3)[0]
        data = AudioSegment.from_mp3("src/" + mp3+".mp3")
        if re.match(".*track[0-9].*", mp3) != None:
            track_no=int(re.sub(".*track([0-9]+)", "\\1", mp3))
            mp3=re.sub("(.*track)[0-9]+", "\\1", mp3)+f"_{track_no:02d}"
            
        print(f"Processing {mp3}")            
        print(f" - segment hunting")
        segments = detect_sound(data, silence_threshold, silence_min_duration)
        
        if len(segments)==0:
            print(f"=== ONLY SILENCE FOUND IN: {mp3}")
            continue
        
        for segment_start, segment_end in segments:
            # Normalize the chunk.
            normalized = data[segment_start:segment_end] #normalize(data[segment_start:segment_end], -18.0)
            
            duration = len(normalized)
            
            print(f"Saving mp3/{mp3}-{int(segment_start):06d}.mp3.")
            normalized.export(f"mp3/{mp3}-{int(segment_start):06d}.mp3",bitrate="192k",format="mp3")
            splits.append(f"mp3/{mp3}-{int(segment_start):06d}.mp3")
    
    with open(output_file, "w") as f:
        for mp3 in splits:
            if os.path.splitext(mp3)[1].lower()!=".mp3":
                continue
            f.write("?") #speaker
            f.write("|")
            f.write(mp3) #audio file
            f.write("|")
            f.write("\n")
            
    sys.exit()