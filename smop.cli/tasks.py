from typing import Tuple, Callable, List, Optional

import os
from os.path import basename, splitext, abspath

from smop import resolve, backend, meta, options
from smop import parser



# filename

class FileInfo:
    input_name: str = ""
    input_disp: str = ""
    output_name: str = ""
    output_disp: str = ""
    
    def __init__(self, input: str, 
                 input_disp: Optional[str] = None, 
                 output: Optional[str] = None, 
                 output_disp: Optional[str] = None
                 ) -> None:
        self.input_name = input
        self.input_disp = input_disp if input_disp else basename(input)
        self.output_name = output if output else splitext(input)[0] + '.py'
        self.output_disp = output_disp if output_disp else basename(self.output_name)
        pass

def rename_basename(fname: str) -> str:
    return splitext(basename(fname))[0] + ".py"

def get_abs_dir(f: str):
    if os.path.isfile(f):
        f = os.path.dirname(f)
    return os.path.abspath(f)

def walk_dir(base_dir: str) -> List[str]:
    fname = []
    for root, _, f_names in os.walk(base_dir):
        for f in f_names:
            fname.append(os.path.normpath(os.path.join(root, f)))
    return fname

def get_abs_norm_path(f: str):
    return os.path.normpath(os.path.abspath(f))

def get_filelist(options: options.Options) -> Tuple[
    List[FileInfo], 
    Callable[[str], bool]]:
    
    filelist: List[FileInfo] = []
    should_exclude: Callable[[str], bool] = lambda _: False
    if options.recurse:

        for dir in options.filelist:
            abs_dir = get_abs_dir(dir)            
            output_dir = os.path.normpath(
                os.path.join(
                    os.path.abspath('.'), 
                    os.path.basename(
                        abs_dir
                    )))
            
            files: List[str] = walk_dir(abs_dir)
            for file in files:
                lfile = file[len(abs_dir):]
                olfile = splitext(lfile)[0] + '.py'
                filelist.append(FileInfo(file, input_disp=lfile, 
                                     output=output_dir + olfile))

        exclude = []
        for edir in options.exclude:
            if os.path.isfile(edir) or os.path.islink(edir):
                exclude.append(get_abs_norm_path(edir))
            elif os.path.isdir(edir):
                for efile in walk_dir(edir):
                     exclude.append(get_abs_norm_path(efile))
                     
        sexclude = set(exclude)
        should_exclude = lambda f: f in sexclude
        
    elif options.glob_pattern:
        pass
    else:
        filelist = [FileInfo(get_abs_norm_path(x)) for x in options.filelist]
        exclude = set([get_abs_norm_path(x) for x in options.xfiles])
        should_exclude = lambda f: basename(f) in exclude
        
    filelist.sort(key=lambda x: x.input_name)
    return filelist, should_exclude

# file       

def read(file: str) -> str:
    buf = open(file, 'r').read()
    buf = buf.replace("\r\n", "\n")
    # FIXME buf = buf.decode("ascii", errors="ignore")
    return buf if buf[-1] == '\n' else buf + '\n'

def convert(src: str, do_resolve: bool = True, do_backend: bool = True) -> str:
    stmt_list = parser.parse(src)
    if not stmt_list:
        return ''
    
    ret: str = ''
    if do_resolve:
        G = resolve.resolve(stmt_list)
    if do_backend:
        ret = backend.backend(stmt_list)
        
    return ret

def get_header(fname: str) -> str:
    return f"# {meta.__header__}\nfrom libsmop import *\n# {fname}\n"
        
def write(file: str, content: str):
    with open(file, 'w') as fp:
        fp.write(content)
    