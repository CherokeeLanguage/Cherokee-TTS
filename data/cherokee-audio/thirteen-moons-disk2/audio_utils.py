
from pydub import AudioSegment

def detect_sound(sound:AudioSegment, silence_threshold:float=-55.0, chunk_size:int=150)->list:
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
        segment_end:int=min(position+chunk_size, len(sound))
        segment_mid:int=min(position+chunk_size/2, len(sound))
        nextChunk:AudioSegment=sound[position:segment_end]
        if sound_start < 0 and nextChunk.dBFS <= silence_threshold:
            continue
        if sound_start < 0:
            sound_start=segment_mid
            continue
        if sound_start >= 0 and nextChunk.dBFS <= silence_threshold:
            segments.append((sound_start, segment_mid))
            sound_start=-1
            continue
        
    if sound_start >= 0:
        segments.append((sound_start, segment_mid))
        
    if len(segments) == 0:
        segments.append((0, len(sound)))
        
    return segments

def combine_segments(segments:list, target_length:int)->list:
    new_segments:list=list()
    
    if len(segments)==0:
        return list()
    
    if len(segments)==1:
        new_segments.append(segments[0])
        return new_segments
    
    start = segments[0][0]
    end = segments[0][1]
    
    for ix in range(1, len(segments)):
        if segments[ix][1] - start < target_length:
            end=segments[ix][1]
            continue
        new_segments.append((start, end))
        start=segments[ix][0]
        end=segments[ix][1]
        
    if new_segments[-1][0] != start:
        new_segments.append((start, end)) 
    
    return new_segments