# Copyright (C) Meilof Veeningen, 2019

import pysnark.libsnark

pb=pysnark.libsnark.protoboard()

def privval(val):
    pbv=pysnark.libsnark.pb_variable()
    pbv.allocate(pb)
    pb.setval(pbv, val)
    return pysnark.libsnark.linear_combination(pbv)

def pubval(val):
    # TODO
    pbv=pysnark.libsnark.pb_variable()
    pbv.allocate(pb)
    pb.setval(pbv, val)
    return pysnark.libsnark.linear_combination(pbv)

def zero():
    return pysnark.libsnark.linear_combination()
    
def one():
    return pysnark.libsnark.linear_combination(1)

def fieldinverse(val):
    return pysnark.libsnark.fieldinverse(val)

def add_constraint(v, w, y):
    #global comphash
    
    pb.add_r1cs_constraint(pysnark.libsnark.r1cs_constraint(v,w,y))
    
    #TODO: check, add to hash
    #comphash = hash((comphash,tuple(v.sig),tuple(w.sig),tuple(y.sig)))
    #if not libsnark.check_mul(v.value, w.value, y.value):
    #    raise ValueError()
    #    needed?
    
    
    
    
    
    