#!/usr/bin/env python3

if __name__ == "__main__":
    import os
    import sys
    
    from chrutils import ced2mco
    
    dname=os.path.dirname(sys.argv[0])
    if len(dname)>0:
        os.chdir(dname)
    
    text:list=list()
    with open("osiyo-tohiju-then-what-ced.txt", "r") as file:
        for line in file:
            text.append(ced2mco(line))
            
    with open("osiyo-tohiju-then-what-mco.txt", "w") as file:
        for line in text:
            file.write(line)

