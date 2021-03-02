#!/usr/bin/env python3

if __name__ == "__main__":
    import os
    import sys
    
    from chrutils import ascii_chrn2mco
    
    dname=os.path.dirname(sys.argv[0])
    if len(dname)>0:
        os.chdir(dname)
    
    text:list=list()
    with open("the-good-samaritan-121.txt", "r") as file:
        for line in file:
            text.append(ascii_chrn2mco(line))
            
    with open("the-good-samaritan-121.mco.txt", "w") as file:
        for line in text:
            file.write(line)

