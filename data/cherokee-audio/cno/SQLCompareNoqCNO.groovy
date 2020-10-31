import groovy.sql.Sql

def SQL = Sql.newInstance( 'jdbc:mysql://localhost/cherokeedictionary?useUnicode=yes&characterEncoding=UTF-8', 'root', 'Tk02030#', 'com.mysql.cj.jdbc.Driver' )

def str = "select * from likespreadsheets where source='cnos'"
def str2 = "select * from likespreadsheets where source != 'cnos' and source != 'cnomed' and source != 'cwl' and source != 'msct' and source != 'ncmed' order by source"

def map = [:]
def f = new File("./list.txt")
f.write("")

class LKS {
    def entrya, syllabaryb, definitiond, source, notes

    @Override
    public String toString() {
        return "LKS{" +
                "entrya=" + entrya +
                ", syllabaryb=" + syllabaryb +
                ", definitiond=" + definitiond +
                ", source=" + source +
                ", notes=" + notes +
                '}';
    }
}

def phoneticList = ["entrya", 'vfirstpresg', 'vsecondimperm', 'vthirdinfo', 'vthirdpresk', 'vthirdpasti']
def syllabaryList = ["syllabaryb", 'vfirstpresh', 'vsecondimpersylln', 'vthirdinfsyllp', 'vthirdpressylll', 'vthirdpastsyllj']
def englishList = ["definitiond"]

def createSQL = {String phonetic, String syllabary, String definition ->
    def sb = new StringBuilder("select * from likespreadsheets where (");
    definition = definition.replace("\'", "")
    phoneticList.each {
        sb << it
        sb << " = '$phonetic' or "
    }

    syllabaryList.each {
        sb << it
        sb << " = '$syllabary' or "
    }

    englishList.each {
        sb << it
        sb << " = '$definition' or "
    }


    sb << "nounadjplurale like '%$phonetic%' "
    sb << "or nounadjpluralsyllf like '%$syllabary%') and (source='ced' or source='rrd')"

    return sb.toString()
}

SQL.eachRow(str) {
    if (it.notes && it.notes.indexOf(".mp3") != -1) {
        def returnv = createSQL(it.entrya, it.syllabaryb, it.definitiond)
        boolean printMain = true;
        String printObject = it;
        SQL.eachRow(returnv) {
            def lks2 = new LKS(entrya: it.entrya, syllabaryb: it.syllabaryb, definitiond: it.definitiond, source: it.source, notes: it.notes)
            if (printMain) {
                f.append(printObject)
                f.append("\n")
                printMain = false;
            }
            map.put(it.id, lks2)
        }
    }
}

/*SQL.eachRow(str) {
    def lks = new LKS(entrya: it.entrya, syllabaryb: it.syllabaryb, definitiond: it.definitiond, source: it.source, notes: it.notes)
    def entry = it.entrya.replaceAll(" ", "").trim().toLowerCase().replaceAll("_", "")
    def definitiond = it.definitiond.replaceAll(" ", "").trim().toLowerCase().replaceAll("_", "")
    def keyValue = String.format("%s_%s", entry, definitiond)

    if (it.notes && it.notes.indexOf(".mp3") != -1) {
        map.put(keyValue, lks)
        count++
    } else {
        if (!map.containsKey(keyValue)) {
            if (it.source == 'cnoS') {
                map.put(keyValue, lks)
            }

            if (!map.containsKey(keyValue)) {
                map.put(keyValue, lks)
            }
        }
    }
}*/

//SQL.eachRow(str2) {
//    def lks = new LKS(entrya: it.entrya, syllabaryb: it.syllabaryb, definitiond: it.definitiond, source: it.source, notes: it.notes)
//    def entry = it.entrya.replaceAll(" ", "").trim().toLowerCase().replaceAll("_", "")
//    def definitiond = it.definitiond.replaceAll(" ", "").trim().toLowerCase().replaceAll("_", "")
//    def keyValue = it.syllabaryb;//String.format("%s_%s", entry, definitiond)
//
//    if (map.containsKey(keyValue)) {
//        if (it.source != 'cnos' && it.source != 'noq') {
//            println lks
//        }
////        if (it.source == 'cnoS') {
////            map.put(keyValue, lks)
////        }
////
////        if (!map.containsKey(keyValue)) {
////            map.put(keyValue, lks)
////        }
//    }
//}

println map.size()

map.each {
    f.append(it.getKey())
    f.append(" ")
    f.append(it.getValue())
    f.append("\n")
}