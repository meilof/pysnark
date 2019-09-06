import pysnark.uselibsnark

backend=pysnark.uselibsnark

class LinComb:
    def __init__(self, val, lc):
        self.val = val
        self.lc = lc
        
    def __mul__(self, other):
        if isinstance(other, LinComb):
            retval = PubVal(self.val*other.val)
            backend.add_constraint_unsafe(self.lc, other.lc, retval.lc)
            return retval

def PubVal(val):
    return LinComb(val, backend.witness(val))
