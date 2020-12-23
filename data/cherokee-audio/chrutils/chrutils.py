#!/usr/bin/env python3
import string
from bleach._vendor.html5lib._ihatexml import letter
from string import ascii_letters
from bleach._vendor.html5lib.constants import asciiLetters
from sre_parse import ASCIILETTERS

def test():
    cedTest = [ "Al¹sda³²yv²hṿ³sga.",
                "U²sgal²sdi ạ²dv¹ne²³li⁴sgi.", 
                "Ụ²wo²³dị³ge⁴ɂi gi²hli a¹ke²³he³²ga na ạ²chu⁴ja.",
                "Ạ²ni²³tạɂ³li ạ²ni²sgạ²ya a¹ni²no²hạ²li²³do³²he, ạ²hwi du¹ni²hyọ²he.", 
                "Sa¹gwu⁴hno ạ²sgạ²ya gạ²lo¹gwe³ ga²ne²he sọ³ɂị³hnv³ hla².",
                "Na³hnv³ gạ²lo¹gwe³ ga²ne⁴hi u²dlv²³kwsạ²ti ge¹se³, ạ²le go²hu⁴sdi yu²³dv³²ne⁴la a¹dlv²³kwsge³.",
                "A¹na³ɂi²sv⁴hnv go²hu⁴sdi wu²³ni³go²he do²jụ²wạ³ɂị²hlv,", 
                "na³hnv³ gạ²lo¹gwe³ ga²ne⁴hi kị²lạ²gwu ị²yv⁴da wị²du²³sdạ³yo²hle³ o²³sdạ²gwu nu²³ksẹ²stạ²nv⁴na ị²yu³sdi da¹sdạ²yo²hị²hv⁴.",
                "U²do²hị²yu⁴hnv³ wu²³yo³hle³ ạ²le u¹ni²go²he³ gạ²nv³gv⁴.",
                "Na³hnv³ gạ²lo¹gwe³ nị²ga²³ne³hv⁴na \"ạ²hwi e¹ni²yo³ɂa!\" u¹dv²hne.",
                "\"Ji²yo³ɂe³²ga\" u¹dv²hne na³ gạ²lo¹gwe³ ga²ne⁴hi, a¹dlv²³kwsgv³.",
                "U¹na³ne²lu²³gi³²se do²jụ²wạ³ɂị²hlv³ di³dla, nạ²ɂv²³hnị³ge⁴hnv wu²³ni³luh²ja u¹ni²go²he³ so²³gwị³li gạɂ³nv⁴.",
                "\"So²³gwị³lị³le³² i¹nạ²da²hị³si\" u¹dv²hne³ na³ u²yo²hlv⁴.", "\"Hạ²da²hị³se³²ga³\" a¹go¹se²³le³." ]
    
    for a in cedTest:
        print("_______________");
        print();
        print(a);
        print(ced2mco(a));
        
    asciiCedText = ["ga.2da.2de3ga","ha.2da.2du1ga","u2da.2di23nv32di","u1da.2di23nv32sv23?i","a1da.2de3go3?i"]
    for a in asciiCedText:
        print("_______________");
        print();
        print(a);
        print(ascii_ced2mco(a));
    return 


def ced2mco(text:str):
    import unicodedata as ud
    import re

    tones2mco = [("²³", "\u030C"), ("³²", "\u0302"), ("¹", "\u0300"), ("²", ""), ("³", "\u0301"), ("⁴", "\u030b")]
    
    text = ud.normalize('NFD', text)
    
    #hack fix for incorrect entries like l1 to ensure correct long vowels
    text = re.sub("(?i)([^aeiouvwy])(¹)", "\\2\\1", text)
    text = re.sub("(?i)([^aeiouvwy])(²³)", "\\2\\1", text)
    text = re.sub("(?i)([^aeiouvwy])(³²)", "\\2\\1", text)
    text = re.sub("(?i)([^aeiouvwy])(⁴)", "\\2\\1", text)
    
    #finish transforming into MCO
    text = re.sub("(?i)([aeiouv])([^¹²³⁴\u0323]+)", "\\1\u0323\\2", text)
    text = re.sub("(?i)([aeiouv])([¹²³⁴]+)$", "\\1\u0323\\2", text)
    text = re.sub("(?i)([aeiouv])([¹²³⁴]+)([^¹²³⁴a-zɂ])", "\\1\u0323\\2\\3", text)
    text = re.sub("(?i)([^aeiouv\u0323¹²³⁴]+)([¹²³⁴]+)", "\\2\\1", text)
    text = re.sub("(?i)([aeiouv])([¹²³⁴]+)", "\\1\\2:", text)
    text = text.replace("\u0323", "")
    text = re.sub("(?i)([aeiouv])²$", "\\1\u0304", text)
    text = re.sub("(?i)([aeiouv])²([^a-zɂ¹²³⁴:])", "\\1\u0304\\2", text)
    #
    for ced2mcotone in tones2mco:
        text = text.replace(ced2mcotone[0], ced2mcotone[1])
    #
    return ud.normalize('NFC', text)

def ascii_ced2mco(text:str):
    import unicodedata as ud
    text = ud.normalize('NFD', text)
    text = text.replace(".", "\u0323")
    text = text.replace("1", "¹")
    text = text.replace("2", "²")
    text = text.replace("3", "³")
    text = text.replace("4", "⁴")
    text = text.replace("?", "ɂ")
    return ced2mco(text)

if __name__ == "__main__":
    test()