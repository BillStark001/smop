from smop import resolve, backend, parse, meta
from os.path import basename, splitext

def read(file: str) -> str:
    buf = open(file, 'r').read()
    buf = buf.replace("\r\n", "\n")
    # FIXME buf = buf.decode("ascii", errors="ignore")
    return buf if buf[-1] == '\n' else buf + '\n'

def convert(src: str, do_resolve: bool = True, do_backend: bool = True) -> str:
    stmt_list = parse.parse(src)
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
        
def rename_basename(fname: str) -> str:
    return splitext(basename(fname))[0] + ".py"
        
def write(file: str, content: str):
    with open(file, 'w') as fp:
        fp.write(content)
    