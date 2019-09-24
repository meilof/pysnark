import sys

from pysnark.runtime import PrivVal

val = int(sys.argv[2])

for i in range(int(sys.argv[1])):
    a = PrivVal(val)
    a*a
