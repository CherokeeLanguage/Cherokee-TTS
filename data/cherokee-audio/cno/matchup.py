#!/usr/bin/env python3

if __name__ == "__main__":
    import os
    import sys
    import csv
    import codecs
    import re
    
    from chrutils import ascii_ced2mco
    from chrutils import ascii_ced2ced
    
    dname=os.path.dirname(sys.argv[0])
    if len(dname)>0:
        os.chdir(dname)
        
    syllabaryList:tuple = ("syllabaryb", 'nounadjpluralsyllf', 'vfirstpresh', 'vsecondimpersylln', 'vthirdinfsyllp', 'vthirdpressylll', 'vthirdpastsyllj')
    pronounceList:tuple = ("entrytone", 'nounadjpluraltone', 'vfirstprestone', 'vsecondimpertone', 'vthirdinftone', 'vthirdprestone', 'vthirdpasttone')
        
    ced:str="ced_202010301607.csv"
    rrd:str="rrd_202010301608.csv"
    cno:str="cnos_202010301611.csv"
    
    ced_lookup:dict=dict()
    rrd_lookup:dict=dict()
    cno_lookup:dict=dict()
    mp3_lookup:dict=dict()
    
    ambig:dict=dict()
    
    # TODO: Split on commas for syll && pron entries
    
    # TODO: Check if CNOS entries ending in 'Ꮫ' will match entries ending in 'Ꮣ'
    
    with open(ced, mode='r', encoding='utf-8-sig') as csvfile:
        records = csv.DictReader(csvfile)
        for record in records:
            for fields in zip(syllabaryList, pronounceList):
                sfield:str=fields[0]
                pfield:str=fields[1]
                value:str=record[sfield].strip()
                pronounce:str=record[pfield].strip()
                if "-" in value or "-" in pronounce:
                    continue
                if len(value)==0:
                    continue
                if len(pronounce)==0:
                    continue                
                if value in ambig.keys():
                    continue
                if value in ced_lookup.keys() and pronounce != ced_lookup[value]:
                    ambig[value]=True
                    ced_lookup.pop(value)
                    continue                
                ced_lookup[value]=pronounce
        
    with open(rrd, mode='r', encoding='utf-8-sig') as csvfile:
        records = csv.DictReader(csvfile)
        for record in records:
            for fields in zip(syllabaryList, pronounceList):
                sfield:str=fields[0]
                pfield:str=fields[1]
                value:str=record[sfield].strip()
                pronounce:str=record[pfield].strip()
                if "-" in value or "-" in pronounce:
                    continue
                if len(value)==0:
                    continue
                if len(pronounce)==0:
                    continue                
                if value in ambig.keys():
                    continue
                if value in rrd_lookup.keys() and pronounce != rrd_lookup[value]:
                    ambig[value]=True
                    rrd_lookup.pop(value)
                    continue
                #convert RRD to CED formatting
                pronounce=re.sub("(?i)([aeiouv])([a-zɂ?])", "\\g<1>2\\g<2>", pronounce, flags=re.IGNORECASE)
                pronounce=re.sub("(?i)([ạẹịọụ])([a-zɂ?])", "\\g<1>2\\g<2>", pronounce, flags=re.IGNORECASE)
                pronounce=re.sub("(?i)(ṿ)([a-zɂ?])", "\\g<1>2\\g<2>", pronounce, flags=re.IGNORECASE)
                rrd_lookup[value]=pronounce
                
    print(f"Skipped loading {len(ambig):,} ambiguous entries from main dictionary files")
    
    with open(cno, mode='r', encoding='utf-8-sig') as csvfile:
        records = csv.DictReader(csvfile)
        for record in records:
            for fields in zip(syllabaryList, pronounceList):
                sfield:str=fields[0]
                pfield:str=fields[1]
                value:str=record[sfield].strip()
                if "-" in value:
                    continue                
                if len(value)==0:
                    continue
                if value in ambig.keys():
                    continue
                if value in ced_lookup.keys():
                    cno_lookup[value]=ced_lookup[value]
                    mp3_lookup[value]=record["notes"]
                    continue
                if value in rrd_lookup.keys():
                    cno_lookup[value]=rrd_lookup[value]
                    mp3_lookup[value]=record["notes"]
                    continue
                if value+"Ꭲ" in ambig.keys():
                    continue
                if value+"Ꭲ" in ced_lookup.keys():
                    pronounce=ced_lookup[value+"Ꭲ"]
                    if pronounce[-1] == "i":
                        pronounce=pronounce[:-1]
                    if pronounce[-1] == "?":
                        pronounce=pronounce[:-1]
                    if pronounce[-1] == "ɂ":
                        pronounce=pronounce[:-1]
                        
                    cno_lookup[value]=pronounce
                    mp3_lookup[value]=record["notes"]
                    continue
                if value+"Ꭲ" in rrd_lookup.keys():
                    rrd_lookup[value+"Ꭲ"]
                    if pronounce[-1] == "i":
                        pronounce=pronounce[:-1]
                    if pronounce[-1] == "?":
                        pronounce=pronounce[:-1]
                    if pronounce[-1] == "ɂ":
                        pronounce=pronounce[:-1]
                    cno_lookup[value]=pronounce
                    mp3_lookup[value]=record["notes"]
                    continue                            

        print(f"Found {len(cno_lookup)} matches.")
        
    with open("matches.txt", "w") as file:
        for key in cno_lookup.keys():
            pronounce=cno_lookup[key]
            mp3=mp3_lookup[key].replace("https://data.cherokee.org/Cherokee/LexiconSoundFiles/", "")
            mco=ascii_ced2mco(pronounce)
            pced=ascii_ced2ced(pronounce)
            print(f"{key}|{mco}|{mp3}|{pronounce}|{pced}",file=file)
        