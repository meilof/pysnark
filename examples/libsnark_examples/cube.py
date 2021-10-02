# from __future__ import print_function

import sys

import pysnark.runtime
from pysnark.runtime import snark, PrivVal

pysnark.runtime.autoprove = False 
pysnark.runtime.operation = "prove" 
@snark
def cube(x):
    return x*x*x

print("The cube of", sys.argv[1], "is", cube(int(sys.argv[1])))

