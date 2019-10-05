# Copyright (C) Meilof Veeningen, 2019

from . import libsnark

pb=libsnark.zks_protoboard_pub()

def privval(val):
    pbv=libsnark.zks_pb_variable()
    pbv.allocate(pb)
    pb.setval(pbv, val)
    return libsnark.zks_linear_combination(pbv)

def pubval(val):
    pbv=libsnark.zks_pb_variable()
    pbv.allocate(pb)
    pb.setpublic(pbv)
    pb.setval(pbv, val)
    return libsnark.zks_linear_combination(pbv)

def zero():
    return libsnark.zks_linear_combination()
    
def one():
    return libsnark.zks_linear_combination(1)

def fieldinverse(val):
    return libsnark.fieldinverse(val)

def get_modulus():
    return libsnark.get_modulus()

def add_constraint(v, w, y):
    pb.add_r1cs_constraint(libsnark.zks_r1cs_constraint(v,w,y))
    
def prove():
    if pb.num_constraints()==0:
        # libsnark does not work in this case, add a no-op
        pb.add_r1cs_constraint(libsnark.zks_r1cs_constraint(libsnark.zks_linear_combination(),libsnark.zks_linear_combination(),libsnark.zks_linear_combination()))
        
    cs=pb.get_constraint_system_pubs()
    pubvals=pb.primary_input_pubs();
    privvals=pb.auxiliary_input_pubs();
    
    print("*** Trying to read pysnark_ek")
    keypair=libsnark.read_key("pysnark_ek", cs)
    if not keypair:
        print("*** No pysnark_key or computation changed, generating keys...")
        keypair=libsnark.zks_generator(cs)
        libsnark.write_keys(keypair, "pysnark_vk", "pysnark_ek")
    
    print("*** PySNARK: generating proof pysnark_log (" +
          "sat=" + str(pb.is_satisfied()) + 
          ", #io=" + str(pubvals.size()) + 
          ", #witness=" + str(privvals.size()) + 
          ", #constraint=" + str(pb.num_constraints()) +
           ")")
    
    proof=libsnark.zks_prover(keypair.pk, pubvals, privvals);
    verified=libsnark.zks_verifier_strong_IC(keypair.vk, pubvals, proof)
    libsnark.write_proof(proof, pubvals, "pysnark_log")
    
    print("*** Public inputs: " + " ".join([str(pubvals.at(i)) for i in range(pubvals.size())]))
    print("*** Verification status:", verified)
    
    