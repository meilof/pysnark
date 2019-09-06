import pysnark.libsnark

pb=pysnark.libsnark.protoboard()

def witness(val):
    pbv=pysnark.libsnark.pb_variable()
    pbv.allocate(pb)
    pb.setval(pbv, val)
    return pysnark.libsnark.linear_combination(pbv)

def add_constraint_unsafe(v, w, y):
    pb.add_r1cs_constraint(pysnark.libsnark.r1cs_constraint(v,w,y))