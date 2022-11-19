import sys
import argparse
from typing import List, Dict, Set

from textwrap import dedent

from smop import meta


class Options:

    filelist: List[str]
    output: str
    exclude: List[str]
    xfiles: Set[str]

    glob_pattern: bool # TODO useless
    recurse: bool # TODO useless
    archive: bool # TODO useless
    
    debug: str

    no_analysis: bool
    no_backend: bool
    no_comments: bool # TODO useless
    no_resolve: bool

    no_header: bool
    no_numbers: bool

    delete_on_error: bool

    strict: bool
    testing_mode: bool

    verbose: bool
    
    def __init__(self) -> None:
        self.filename = ""
        self.debug_main = False
        self.debug_lexer = False
        self.debug_parser = False
        self.xfiles = []
    
    def parse_args(self):
        
        self.exclude = self.exclude if self.exclude else []
        self.xfiles = set(self.exclude)
        
        self.debug = self.debug.lower() if self.debug else ''
        self.debug_main = 'm' in self.debug
        self.debug_lexer = 'l' in self.debug
        self.debug_parser = 'p' in self.debug


def make_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        meta.__package_cmd__,
        usage=meta.__desc_usage__,
        description=meta.__desc__,
        epilog=meta.__example__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("filelist", nargs="*", metavar="file.m", type=str)
    parser.add_argument("-o", "--output", metavar="FILE.py", type=str, help="""
    Write the results to FILE.py.  Use -o- to send the results to the
    standard output.  If not specified explicitly, output file names are
    derived from input file names by replacing ".m" with ".py".  
    For example,
    
        $ smop FILE1.m FILE2.m FILE3.m
        
    generates files FILE1.py FILE2.py and FILE3.py
    """)
    parser.add_argument("-x", "--exclude", nargs="*", 
                        metavar="FILE1.m,FILE2.m,FILE3.m", type=str, help="""
    comma-separated list of files to ignore
    """)
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-r", "--recurse", action='store_true', help="""
    Convert files recursively. If assigned true, the files and output
    will be treated as folders.
    Example:
    
        $ smop octave-4.0.2 -r""")
    group.add_argument("-g", "--glob-pattern", action="store_true", help="""
    Search files to convert applying unix glob pattern to the input file 
    list or to files. 
    Example:
    
        $ smop octave-4.0.2/*.m -g """)


    parser.add_argument("-V", '--version', action='version',
                        version=meta.__version__)

    
    parser.add_argument("-Z", "--archive", metavar="ARCHIVE.tar", help="""
    Read ".m" files from the archive; ignore other files.  Accepted
    format: "tar".  Accepted compression: "gzip", "bz2".
    """)

    parser.add_argument("-D", "--debug", help="""
    Enable built-in debugging tools in corresponding stages if the 
    following codes are assigned.
        M: Main
        L: Lex
        P: Parse
    """)
    
    parser.add_argument("-A", "--no-analysis", action="store_true", help="""
    skip analysis
    """)
    parser.add_argument("-B", "--no-backend", action="store_true", help="""
    omit code generation
    """)
    parser.add_argument("-C", "--no-comments", action="store_true", help="""
    discard multiline comments""")
    parser.add_argument("-R", "--no-resolve", action="store_true", help="""
    omit name resolution
    """)

    parser.add_argument("-H", "--no-header", action="store_true", help="""
    use it if you plan to concatenate the generated files
    """)
    parser.add_argument("-N", "--no-numbers", action="store_true", help="""
    discard line-numbering information
    """)

    parser.add_argument("-E", "--delete-on-error", action="store_false", help="""
    By default, broken ".py" files are kept alive to allow their
    examination and debugging. Sometimes we want the opposite behavior""")

    parser.add_argument("-S", "--strict", action="store_true", help="""
    stop after first syntax error (by default compiles other .m files)
    """)
    parser.add_argument("-T", "--testing-mode", action="store_true", help="""
    support special "testing" percent-bang comments used to write Octave
    test suite.  When disabled, behaves like regular comments
    """)

    parser.add_argument("-v", "--verbose", action="store_true", help="""
    Print extra information while converting""")

    return parser

options = Options()
args = make_parser().parse_args(namespace=options)
options.parse_args()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
