import pysnark.libsnark

class LinComb:
    def __init__(self, val, lc):
        self.val = val
        self.lc = lc
        
    def __mul__(self, other):
        if isinstance(other, LinComb):
            retval = PubVal(self.val*other.val)
            pb.add_r1cs_constraint(pysnark.libsnark.r1cs_constraint(self.lc, other.lc, retval.lc))
            return retval

def PubVal(val):
    pbv=pysnark.libsnark.pb_variable()
    pbv.allocate(pb)
    pb.setval(pbv, val)
    return LinComb(val, pysnark.libsnark.linear_combination(pbv))

pb=pysnark.libsnark.protoboard()

