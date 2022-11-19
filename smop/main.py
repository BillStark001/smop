# SMOP -- Simple Matlab/Octave to Python compiler
# Copyright 2011-2016 Victor Leikehman

from __future__ import print_function

import py_compile
import tempfile
import fnmatch
import tarfile
import sys
from os.path import basename, splitext
import traceback

from smop.options import options
from smop import parse
from smop import resolve
from smop import backend
from smop import meta
from smop import tasks


def print_header(fp):
    if options.no_header:
        return
    #print("# Running Python %s" % sys.version, file=fp)
    print("# Generated with SMOP ", meta.__version__, file=fp)
    print("from libsmop import *", file=fp)
    print("#", options.filename, file=fp)


def main():
    if "M" in options.debug:
        import pdb
        pdb.set_trace()
    if not options.filelist:
        options.parser.print_help()
        return
    if options.output == "-":
        fp = sys.stdout
    elif options.output:
        fp = open(options.output, "w")
    else:
        fp = None
    if fp:
        print_header(fp)

    nerrors = 0
    for i, options.filename in enumerate(options.filelist):
        try:
            if options.verbose:
                print(i, options.filename)
            if not options.filename.endswith(".m"):
                print("\tIgnored: '%s' (unexpected file type)" %
                      options.filename)
                continue
            if basename(options.filename) in options.xfiles:
                if options.verbose:
                    print("\tExcluded: '%s'" % options.filename)
                continue
            buf = tasks.read(options.filename)
            ret = tasks.convert(
                buf, 
                do_backend=not options.no_backend, 
                do_resolve=not options.no_resolve
                )
            
            if not options.output:
                output_name = tasks.rename_basename(options.filename)
                output_path = output_name # TODO
                if not options.no_header:
                    ret = tasks.get_header(options.filename)
                tasks.write(output_path, ret)
            else:
                fp.write(ret)
                
        except KeyboardInterrupt:
            break
        except:
            nerrors += 1
            traceback.print_exc(file=sys.stdout)
            if options.strict:
                break
        finally:
            pass
    if nerrors:
        print("Errors:", nerrors)
