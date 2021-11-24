

import os
import sys

if __name__ == "__main__":

    workdir: str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    workdir = os.getcwd()

    lang_counts: dict = dict()

    with open("all.txt", "r") as f:
        for line in f:
            fields = line.split("|")
            if len(fields) < 2:
                continue
            lang = fields[2]
            if not lang in lang_counts.keys():
                lang_counts[lang] = 0
            lang_counts[lang] = lang_counts[lang] + 1

    counts_list: list = list()
    for key in lang_counts.keys():
        counts_list.append((key, lang_counts[key]))

    counts_list.sort(key=lambda value: value[1], reverse=True)

    langs: set = set()
    with open("train.txt", "r") as f:
        for line in f:
            fields = line.split("|")
            lang = fields[2]
            if lang in langs:
                continue
            langs.add(lang)

    with open("langs.txt", "w") as f:
        for lang_count in counts_list:
            lang: str = lang_count[0]
            if not lang in langs:
                continue
            f.write(f"{lang_count[0]}: {int(lang_count[1]):,}")
            f.write("\n")
