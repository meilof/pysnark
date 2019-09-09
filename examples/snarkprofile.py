from cProfile import Profile
import pstats
import os
import sys

from optparse import OptionParser

usage = "profile.py [-o output_file_path] [-s sort] scriptfile [arg] ..."
parser = OptionParser(usage=usage)
parser.allow_interspersed_args = False
#parser.add_option('-o', '--outfile', dest="outfile",
#    help="Save stats to <outfile>", default=None)
#parser.add_option('-s', '--sort', dest="sort",
#    help="Sort order when printing to stdout, based on pstats.Stats class",
#    default=-1)

if not sys.argv[1:]:
    parser.print_usage()
    sys.exit(2)

(options, args) = parser.parse_args()
sys.argv[:] = args

if len(args) > 0:
    progname = args[0]
    sys.path.insert(0, os.path.dirname(progname))
    with open(progname, 'rb') as fp:
        code = compile(fp.read(), progname, 'exec')
    globs = {
        '__file__': progname,
        '__name__': '__main__',
        '__package__': None,
        '__cached__': None,
    }
    
    import pysnark.runtime

    __acu = pysnark.runtime.add_constraint_unsafe
    constraints = 0
    def myacu(*args, **kwargs):
        global constraints
        constraints += 1
        __acu(*args, **kwargs)
    pysnark.runtime.add_constraint_unsafe = myacu

    profiler = Profile(lambda: constraints)
    profiler.runctx(code, globs, None)
    result = pstats.Stats(profiler)
    result.sort_stats("time")
    result.print_stats()
else:
    parser.print_usage()

