from smop import lexer
from smop.options import options
import sys

if __name__ == "__main__":
    options.testing_mode = 0
    options.debug_lexer = 0
    lexer1 = lexer.new()
    buf = open(sys.argv[1]).read()
    lexer1.input(buf)
    for tok in lexer1:
        print(tok)