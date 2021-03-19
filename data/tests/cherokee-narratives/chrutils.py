#!/usr/bin/env python3
import string

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
        #print("_______________");
        #print();
        #print(a);
        #print(ced2mco(a));
        pass
        
    chrnTest = [ ]
    
    for a in chrnTest:
        #print("_______________");
        #print();
        #print(a);
        #print(chrn2mco(a));
        pass
        
    asciiChrnText = ["ji23sa.3hno ju23hne4jv hi.?a nuwese23le3?i kilo3",
                    "iyu4sdi",
                    "ji.lu3si.li.mi u23hni.3gise3",
                    "jeligo uwenv3se3?i",
                    "dina.dah23nsa.hvsgi.3hno duna.dahwantvhta.ne.3?i",
                    "de23gv3wahnuwe3se3 duhnuwa.3?v4?i",
                    "nasgi a.le3 gvwa.li3?vhni.3le?i a.le3 una.da.3nvse3",
                    "gvwa.de3je3 a.ye4li",
                    "i.yv4dv uyohusv4hi gese3i a.yeli.hno",
                    "nuwvta.ne3 ki.lo3 i.yu4sdi aji23lv.ge23lo.hi nahna",
                    "niga.3nv3hnv di.3?ulose3? ugo23hnv.hno a3hni3didlv.3gwo nu3lose3?i",
                    "a.le3 nasgwo a.li23wi nahna3 edo3hv",
                    "uluh3je3 u.ktahne3?i",
                    "a.le3 a3hni.3di3dlv.3gwo nu23lo3se3?i ki.lo23sgi.ni3",
                    "i.yu4sdi sa.meli4yi e4hi a3?isv4?i uluh3je3",
                    ]
    for a in asciiChrnText:
        print("_______________");
        print();
        print(a);
        print(ascii_chrn2mco(a));
    return 


def ced2mco(text:str)->str:
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

def ascii_ced2mco(text:str)->str:
    import unicodedata as ud
    text = ud.normalize('NFD', text)
    text = text.replace(".", "\u0323")
    text = text.replace("1", "¹")
    text = text.replace("2", "²")
    text = text.replace("3", "³")
    text = text.replace("4", "⁴")
    text = text.replace("?", "ɂ")
    return ced2mco(text)

def ascii_chrn2mco(text:str)->str:
    import unicodedata as ud
    text = ud.normalize('NFD', text)
    text = text.replace(".", "\u0323")
    text = text.replace("1", "¹")
    text = text.replace("2", "²")
    text = text.replace("3", "³")
    text = text.replace("4", "⁴")
    text = text.replace("?", "ɂ")
    return chrn2mco(text)

def chrn2mco(text:str)->str:
    import regex as re
    import unicodedata as ud
    text = ud.normalize('NFD', text)
    
    text = re.sub("(?i)([h])([¹²³⁴][¹²³⁴])", "\\2\\1", text)
    text = re.sub("(?i)([h])([¹²³⁴])", "\u0323\\2\\1", text)
    
    text = re.sub("(?i)([ɂ])([¹²³⁴][¹²³⁴])", "\\2\\1", text)
    text = re.sub("(?i)([ɂ])([¹²³⁴])", "\u0323\\2\\1", text)
    
    text = re.sub("(?i)([aeiouv\u0323]+)([^aeiouv\u0323])([¹²³⁴]+)", "\\1\\3\\2", text)
    text = re.sub("(?i)([aeiouv]\u0323)([^ ¹²³⁴,])(.)", "\\1"+"²"+"\\2\\3", text)
    text = re.sub("(?i)([aeiouv])([^ ¹²³⁴\u0323,])(.)", "\\1"+"²"+"\\2\\3", text)
    return ced2mco(text)

if __name__ == "__main__":
    test()