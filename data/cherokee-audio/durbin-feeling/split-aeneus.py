#!/usr/bin/env python3

import os
import sys
import string
import unicodedata as ud
import random
import re
import pathlib
import subprocess
from shutil import rmtree
import json


#https://www.readbeyond.it/aeneas/docs/libtutorial.html
from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from aeneas.runtimeconfiguration import RuntimeConfiguration

# https://stackoverflow.com/questions/45526996/split-audio-files-using-silence-detection

# Import the AudioSegment class for processing audio and the 
# split_on_silence function for separating out silent chunks.
from pydub import AudioSegment
from pydub.silence import split_on_silence

# From https://stackoverflow.com/questions/29547218/
# remove-silence-at-the-beginning-and-at-the-end-of-wave-files-with-pydub
from pydub import AudioSegment


def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms
    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0  # ms
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
        trim_ms += chunk_size

    return trim_ms

# Define a function to normalize a chunk to a target amplitude.
def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)

if __name__ == "__main__":
    
    from chrutils import ced2mco
    from chrutils import mco2espeak
         
    workdir:string = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()
    
    mp3Dir:str="mp3-aligned"

    #clean up any previous files
    rmtree(mp3Dir, ignore_errors=True)
    os.mkdir(mp3Dir)
    
    
    from os import walk
    mp3s = []
    for (dirpath, dirnames, filenames) in walk("src"):
        mp3s.extend(filenames)
        break
    mp3s.sort()
    
    with open("ma-aeneas.txt", "w") as f:
        f.write("")

    splits:list=[]
    for mp3 in mp3s:
        
        if os.path.splitext(mp3)[1].lower()!=".mp3":
            continue
        transcript:str=os.path.splitext(mp3)[0]+".txt"
        
        mp3=os.path.abspath("src/"+mp3)
        transcript=os.path.abspath("src-transcripts/"+transcript)
        
        if not os.path.exists(transcript):
                print(f" - Transcript {os.path.basename(transcript)} not found - skipping")
                continue
        
        revEspeakLookup:dict={}
        tLines:list=[]
        with open(transcript, "r") as f:
            for line in f:
                tLines.append(line.strip())
        with open("espeak.txt", "w") as f:
            for line in tLines:
                espeak:str=mco2espeak(line)
                revEspeakLookup[espeak]=line
                f.write(espeak)
                f.write("\n")
        
        print(f"Processing {os.path.basename(mp3)}")
    
        config:str="task_language=eng"
        config +="|is_text_type=plain"
        config +="|os_task_file_format=json"
        config +="|"+RuntimeConfiguration.MFCC_MASK_NONSPEECH+"=True"
        config +="|"+RuntimeConfiguration.MFCC_MASK_NONSPEECH_L3+"=True"
#        config +="|os_task_file_levels=123"
        
        config +="|task_adjust_boundary_nonspeech_min=0.01"
        config +="|task_adjust_boundary_nonspeech_string=(sil)"
        
        config +="|is_audio_file_detect_head_max=1.50"
        config +="|is_audio_file_detect_tail_max=1.50"
        
        task:Task = Task(config_string=config)
        task.audio_file_path_absolute=mp3
        task.text_file_path_absolute="espeak.txt"
        task.sync_map_file_path_absolute="alignments.txt"
        
        ExecuteTask(task).execute()
        task.output_sync_map_file()
        
        audioData = AudioSegment.from_mp3(mp3)
        
        i=0;
        with open("alignments.txt") as f:
            alignments = json.load(f)
            for fragment in alignments["fragments"]:
                if fragment["id"][0]=="n":
                    continue
                i+=1
                begin=max(0,int((float(fragment["begin"])-.1)*1000)) #milliseconds
                end=min(len(audioData),max(0,int((float(fragment["end"])+.2)*1000))) #milliseconds
                segment=audioData[begin:end]
                segment=match_target_amplitude(segment, -16.0)
                segment.export(f"mp3-aligned/{os.path.basename(mp3)}-{i:03d}.mp3",bitrate="192k",format="mp3")
                splits.append(f"mp3-aligned/{os.path.basename(mp3)}-{i:03d}.mp3")
                phrases:list=fragment["lines"]
                text:str=""
                for phrase in phrases:
                    tmp=revEspeakLookup[phrase]
                    if len(text)>0:
                        text+=" "
                    text+=tmp
                with open("ma-aeneas.txt", "a") as f:
                    f.write("?") #speaker
                    f.write("|")
                    f.write(f"mp3-aligned/{os.path.basename(mp3)}-{i:03d}.mp3") #audio file
                    f.write(f"|{text}")
                    f.write("\n")       
            
    #cleanup
    for file in ["alignments.txt", "espeak.txt"]:
        if os.path.exists(file):
            os.remove(file)

    sys.exit()