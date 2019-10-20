# Copyright (C) Meilof Veeningen, 2019

import sys

import libsnark.alt_bn128 as libsnark

pb=libsnark.ProtoboardPub()

def privval(val):
    pbv=libsnark.PbVariable()
    pbv.allocate(pb)
    pb.setval(pbv, val)
    return libsnark.LinearCombination(pbv)

def pubval(val):
    pbv=libsnark.PbVariable()
    pbv.allocate(pb)
    pb.setpublic(pbv)
    pb.setval(pbv, val)
    return libsnark.LinearCombination(pbv)

def zero():
    return libsnark.LinearCombination()
    
def one():
    return libsnark.LinearCombination(1)

def fieldinverse(val):
    return libsnark.fieldinverse(val)

def get_modulus():
    return libsnark.get_modulus()

def add_constraint(v, w, y):
    pb.add_r1cs_constraint(libsnark.R1csConstraint(v,w,y))
    
use_groth=False

def prove(do_keygen=True, do_write=True, do_print=True):
    if pb.num_constraints()==0:
        # libsnark does not work in this case, add a no-op
        pb.add_r1cs_constraint(libsnark.R1csConstraint(libsnark.LinearCombination(),libsnark.LinearCombination(),libsnark.LinearCombination()))
        
    cs=pb.get_constraint_system_pubs()
    pubvals=pb.primary_input_pubs()
    privvals=pb.auxiliary_input_pubs()
    
    read_key           = (libsnark.zkgg_read_key if use_groth else libsnark.zk_read_key)
    generator          = (libsnark.zkgg_generator if use_groth else libsnark.zk_generator)
    write_keys         = (libsnark.zkgg_write_keys if use_groth else libsnark.zk_write_keys)
    prover             = (libsnark.zkgg_prover if use_groth else libsnark.zk_prover)
    verifier_strong_IC = (libsnark.zkgg_verifier_strong_IC if use_groth else libsnark.zk_verifier_strong_IC)
    write_proof        = (libsnark.zkgg_write_proof if use_groth else libsnark.zk_write_proof)
    
    if do_print: print("*** Trying to read pysnark_ek", file=sys.stderr)
    keypair=read_key("pysnark_ek", cs)
    if not keypair:
        if do_keygen:
            if do_print: print("*** No pysnark_ek or computation changed, generating keys...", file=sys.stderr)
            keypair=generator(cs)
            write_keys(keypair, "pysnark_vk", "pysnark_ek")
        else:
            raise RuntimeError("*** No pysnark_ek or key is for different computation")
        
    if do_print: 
        print("*** PySNARK: generating proof pysnark_log (" +
              "sat=" + str(pb.is_satisfied()) + 
              ", #io=" + str(pubvals.size()) + 
              ", #witness=" + str(privvals.size()) + 
              ", #constraint=" + str(pb.num_constraints()) +
              ")", file=sys.stderr)
    
    proof=prover(keypair.pk, pubvals, privvals);
    if do_write: write_proof(proof, pubvals, "pysnark_log")

    if do_print: print("*** Public inputs: " + " ".join([str(pubvals.at(i)) for i in range(pubvals.size())]), file=sys.stderr)
    if do_print: print("*** Verification status:", verifier_strong_IC(keypair.vk, pubvals, proof), file=sys.stderr)
    
    return (keypair.vk, proof, pubvals)
    
    