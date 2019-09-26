#!/usr/bin/env python3

import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", default="qsurveytools.exe")
    parser.add_argument("--dir", default="bin")
    args = parser.parse_args()
    exepath = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), args.dir, args.exe)
    subprocess.Popen([exepath])
    return 0

if __name__ == "__main__":
    sys.exit(main())
