import sys

from pysnark.runtime import PrivVal

x = PrivVal(int(sys.argv[1]))
for _ in range(int(sys.argv[2])):
    x = (x*x) % 256