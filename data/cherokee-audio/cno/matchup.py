#!/usr/bin/env python3

if __name__ == "__main__":
    import os
    import sys
    import csv
    import codecs
    
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
    
    ambig:dict=dict()
    
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
                    continue
                if value in rrd_lookup.keys():
                    cno_lookup[value]=rrd_lookup[value]
                    continue
                if value+"Ꭲ" in ambig.keys():
                    continue
                if value+"Ꭲ" in ced_lookup.keys():
                    cno_lookup[value]=ced_lookup[value+"Ꭲ"]
                    continue
                if value+"Ꭲ" in rrd_lookup.keys():
                    cno_lookup[value]=rrd_lookup[value+"Ꭲ"]
                    continue                            

        print(f"Found {len(cno_lookup)} matches.")
        