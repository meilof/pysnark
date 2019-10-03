from pysnark.branching import if_then_else, BranchingValues, _if, _range, _endfor
from pysnark.runtime import PrivVal

_=BranchingValues()
_.ret=1
n=PrivVal(5)
for i in _range(2,n+1,max=8):
    _.ret=_.ret*i
_endfor()
_.ret
