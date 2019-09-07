# (C) Meilof Veeningen, 2019

import sys

from pysnark.runtime import PrivVal

val1 = PrivVal(10)
	
print(val1<7)    # false
print(val1<8)    # false
print(val1<9)    # false
print(val1<10)   # false
print(val1<11)   # true
print(val1<12)   # true
    
print(val1<PrivVal(7))    # false
print(val1<PrivVal(8))    # false
print(val1<PrivVal(9))    # false
print(val1<PrivVal(10))   # false
print(val1<PrivVal(11))   # true
print(val1<PrivVal(12))   # true
    
