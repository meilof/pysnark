
# from __future__ import print_function

import sys

from pysnark.libsnark.backend import verify_only
print("Verification of proof", sys.argv[1], "pubvals ", sys.argv[2], "using verification key", sys.argv[3]," is ", verify_only(sys.argv[3],sys.argv[2],sys.argv[1]))

