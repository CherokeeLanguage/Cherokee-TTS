#!/usr/bin/env -S conda run -n denoiser python
import os
import sys

if __name__ == "__main__":
    orig_dir: str = "../Audio Files"
    workdir: str = os.path.dirname(sys.argv[0])
    if workdir.strip() != "":
        os.chdir(workdir)
    print(workdir)
    workdir = os.getcwd()
    original_files: list = list()
    for (dirpath, dirnames, filenames) in os.walk(orig_dir):
        print(dirpath)
        print(dirnames)
        print(filenames)
        for filename in filenames:
            original_files.append(os.path.join(dirpath, filename))

    print(original_files)