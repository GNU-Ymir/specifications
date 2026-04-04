#!/usr/bin/env python3

import argparse
import shutil
import glob
import pathlib
from pathlib import Path
import os
import subprocess

def rebuildDir ()-> None:
    shutil.rmtree (".doc", ignore_errors=True)
    Path (".doc").mkdir (exist_ok=True, parents=True)
    
    files = [y for x in os.walk("src/") for y in glob.glob(os.path.join(x[0], '*.org'))]
    relPath = "src/"

    for f in files :
        dstPath = Path (".doc") / (os.path.splitext (os.path.relpath (f, relPath))[0] + ".md")
        dstPath.parent.mkdir (exist_ok=True, parents=True)
        
        subprocess.call (["pandoc", "-f", "org", "-t", "gfm", f, "-o", str (dstPath)])

    shutil.copy (Path ("src/conf.py"), Path (".doc/"))
    shutil.copy (Path ("src/index.rst"), Path (".doc/"))
    shutil.copytree (Path ("src/_static"), Path (".doc/_static"))
    shutil.copytree (Path ("src/_template"), Path (".doc/_template"))
        
    
def main (args: argparse.Namespace)-> None:
    rebuildDir ()
    subprocess.call (["sphinx-build", "-b", "html", ".doc/", ".doc/_build/html"])
    
def parseArguments ()-> argparse.Namespace:
    parser = argparse.ArgumentParser ()
    parser.add_argument ("-b", help="build", action="store_true")
    parser.add_argument ("-l", help="listen", action="store_true")

    return parser.parse_args ()
    
if __name__ == "__main__":
    args = parseArguments ()    
    main (args)
