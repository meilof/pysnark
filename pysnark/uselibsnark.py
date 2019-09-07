# Copyright (C) Meilof Veeningen, 2019

import pysnark.libsnark

pb=pysnark.libsnark.protoboard_pub()

def privval(val):
    pbv=pysnark.libsnark.pb_variable()
    pbv.allocate(pb)
    pb.setval(pbv, val)
    return pysnark.libsnark.linear_combination(pbv)

def pubval(val):
    pbv=pysnark.libsnark.pb_variable()
    pbv.allocate(pb)
    pb.setpublic(pbv)
    pb.setval(pbv, val)
    return pysnark.libsnark.linear_combination(pbv)

def zero():
    return pysnark.libsnark.linear_combination()
    
def one():
    return pysnark.libsnark.linear_combination(1)

def fieldinverse(val):
    return pysnark.libsnark.fieldinverse(val)

def get_modulus():
    return pysnark.libsnark.get_modulus()

def add_constraint(v, w, y):
    #global comphash
    
    pb.add_r1cs_constraint(pysnark.libsnark.r1cs_constraint(v,w,y))
    
    #TODO: check, add to hash
    #comphash = hash((comphash,tuple(v.sig),tuple(w.sig),tuple(y.sig)))
    #if not libsnark.check_mul(v.value, w.value, y.value):
    #    raise ValueError()
    #    needed?
    
def prove():
    cs=pb.get_constraint_system_pubs()
    pubvals=pb.primary_input_pubs();
    privvals=pb.auxiliary_input_pubs();
    
    print("sat", pb.is_satisfied())
    #print(pysnark.libsnark.r1cs_ppzksnark_generator(cs))
    keypair=pysnark.libsnark.read_key_or_generate(cs, "pysnark_ek", "pysnark_vk")
    
    print("*** PySNARK: generating proof pysnark_log (" +
          "#io=" + str(pubvals.size()) + 
          ", #witness=" + str(privvals.size()) + 
          ", #constraint=" + str(pb.num_constraints()) +
           ")")
    
    proof=pysnark.libsnark.r1cs_ppzksnark_prover(keypair.pk, pubvals, privvals);
    verified=pysnark.libsnark.r1cs_ppzksnark_verifier_strong_IC(keypair.vk, pubvals, proof);
    
    print("*** Public inputs: " + " ".join([str(pubvals.at(i)) for i in range(pubvals.size())]))

    #cerr << "*** Public inputs:";
    #for (auto &v: pubvals) cerr << " " << v;
    #cerr << endl;
    print("*** Verification status:", verified)
    
    