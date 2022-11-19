import os
import io
import sys


def __is_text_file(fp):
    return isinstance(fp, io.TextIOBase)


def fopen(*args):
    try:
        fp = open(*args)
        assert fp != -1
        return fp
    except:
        return -1


def fflush(fp):
    fp.flush()


def fprintf(fp, fmt, *args):
    if not __is_text_file(fp):
        fp = sys.stdout
    fp.write(str(fmt) % args)


def fullfile(*args):
    return os.path.join(*args)


def exist(a, b):
    if str(b) == 'builtin':
        return str(a) in globals()
    if str(b) == 'file':
        return os.path.exists(str(a))
    raise NotImplementedError
