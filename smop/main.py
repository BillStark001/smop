# SMOP -- Simple Matlab/Octave to Python compiler
# Copyright 2011-2016 Victor Leikehman

from typing import Optional
from io import TextIOBase

import py_compile
import tempfile
import fnmatch
import tarfile
import sys
import os
import traceback

from smop.options import options
from smop import parse
from smop import resolve
from smop import backend
from smop import meta
from smop import tasks

def convert(finfo: tasks.FileInfo, 
          i: int = -1, fp: Optional[TextIOBase] = None):
    options.filename = finfo.input_name
    
    if not options.filename.endswith(".m"):
        print(f"Ignored: '{finfo.input_disp}' (unexpected file type)")
        return
    
    if options.verbose:
        print(f"Parsing: '{finfo.input_disp} -> {finfo.output_disp} (#{i})")
    
    buf = tasks.read(options.filename)
    ret = tasks.convert(
        buf, 
        do_backend=not options.no_backend, 
        do_resolve=not options.no_resolve
        )
    
    if not options.no_header:
        ret = tasks.get_header(options.filename) + ret
    
    if not fp:
        os.makedirs(os.path.dirname(finfo.output_name), exist_ok=True)
        tasks.write(finfo.output_name, ret)
    else:
        fp.write(ret)
    

def main():
    
    if options.debug_main:
        # debug mode activated
        import pdb
        pdb.set_trace()
    
    if not options.filelist:
        # no input assigned
        options.parser.print_help()
        return
    
    fp: Optional[TextIOBase] = None
    nr_err: int = 0
    
    if options.output == "-":
        fp = sys.stdout
    elif options.output:
        try:
            fp = open(options.output, "w")
        except:
            nr_err += 1
            print("ERROR --output") # TODO format

    filelist, should_exclude = tasks.get_filelist(options)
    
    for i, finfo in enumerate(filelist):
        try:
            if should_exclude(finfo.input_name):
                if options.verbose:
                    print(f"Excluded: '{finfo.input_disp}'")
                continue
            
            convert(finfo, i=i, fp=fp)
                
        except KeyboardInterrupt:
            break
        except:
            nr_err += 1
            traceback.print_exc(file=sys.stdout)
            if options.strict:
                break
        finally:
            pass
    if nr_err:
        print("Errors:", nr_err)
