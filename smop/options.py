import sys
import argparse
from typing import List, Dict, Tuple

from textwrap import dedent

from smop import meta


class Options:

    filelist: List[str]
    output: str
    exclude: str
    xfiles: List[str]

    glob_pattern: str
    archive: bool

    debug: List[str]
    debug_lexer: bool
    debug_parser: bool

    no_analysis: bool
    no_backend: bool
    no_comments: bool
    no_resolve: bool

    no_header: bool
    no_numbers: bool

    delete_on_error: bool

    strict: bool
    testing_mode: bool

    verbose: bool
    
    def __init__(self) -> None:
        self.filename = ""
    
    def parse_args(self):
        self.xfiles = self.exclude.split(",") if args.exclude else []
        self.debug = self.debug.split(":") if args.debug else []


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
    derived from input file names by replacing ".m" with ".py".  For example,

        $ smop FILE1.m FILE2.m FILE3.m

    generates files FILE1.py FILE2.py and FILE3.py
    """)

    parser.add_argument("-x", "--exclude", metavar="FILE1.m,FILE2.m,FILE3.m", type=str, help="""
    comma-separated list of files to ignore
    """)

    parser.add_argument("-V", '--version', action='version',
                        version=meta.__version__)

    parser.add_argument("-g", "--glob-pattern", metavar="PATTERN", type=str, help="""
    Apply unix glob pattern to the input file list or to files. For
    example -g 'octave-4.0.2/*.m""")
    parser.add_argument("-Z", "--archive", metavar="ARCHIVE.tar", help="""
    Read ".m" files from the archive; ignore other files.  Accepted
    format: "tar".  Accepted compression: "gzip", "bz2".
    """)

    parser.add_argument("-D", "--debug", help="""
    Colon-separated codes.
    M Main
    L Lex
    P Parse
    """)
    parser.add_argument("-L", "--debug-lexer", action="store_true", help="""
    enable built-in debugging tools
    """)
    parser.add_argument("-P", "--debug-parser", action="store_true", help="""
    enable built-in debugging tools
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

    parser.add_argument("-v", "--verbose", action="store_true")

    return parser

options = Options()
args = make_parser().parse_args(namespace=options)
options.parse_args()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
