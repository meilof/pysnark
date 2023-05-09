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



keygen_pk_file = "pysnark_pk"
keygen_vk_file = "pysnark_vk"

prover_pk_file = "pysnark_pk"
prover_proof_file = "pysnark_proof"
prover_pubvals_file = "pysnark_pubvals"

verifier_vk_file = "pysnark_vk"
verifier_proof_file = "pysnark_proof"
verifier_pubvals_file = "pysnark_pubvals"

def process_snark(operation,namevals):

    global keygen_pk_file,keygen_vk_file,prover_pk_file,prover_proof_file,prover_pubvals_file,verifier_vk_file,verifier_proof_file,verifier_pubvals_file
    keygen_only_flag=False
    prove_only_flag=False
    verify_only_flag=False

    if operation=="keygen": 
        keygen_only_flag=True
        if keygen_pk_file in namevals: keygen_pk_file=namevals[keygen_pk_file]
        if keygen_vk_file in namevals: keygen_pk_file=namevals[keygen_vk_file]
    elif operation=="prove": 
        prove_only_flag=True
        if prover_pk_file in namevals: prover_pk_file=namevals[prover_pk_file]
        if prover_proof_file in namevals: prover_proof_file=namevals[prover_proof_file]
        if prover_pubvals_file in namevals: prover_pubvals_file=namevals[prover_pubvals_file]
    elif operation=="verify":
        verify_only_flag=True
        if verifier_vk_file in namevals: verifier_vk_file=namevals[verifier_vk_file]
        if verifier_proof_file in namevals: verifier_proof_file=namevals[verifier_proof_file]
        if verifier_pubvals_file in namevals: verifier_pubvals_file=namevals[verifier_pubvals_file]
    else: 
        print("Unrecognised operation",operation)
        return

    if keygen_only_flag: 
       retval = (pk,vk)= keygen_only(keygen_pk_file,keygen_vk_file)   #(pk,vk)
    elif prove_only_flag: 
       retval = prove_only(prover_pk_file,prover_proof_file,prover_pubvals_file) #(proof,pubvals)
    elif verify_only_flag: 
        retval=verify_only(verifier_vk_file,verifier_pubvals_file,verifier_proof_file)
        print("Verified ?",retval)

    return retval

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
		
    mod = libsnark.get_modulus()
    modd2 = mod//2
    def rounded(val): return val if val<=modd2 else val-mod

    if do_print: print("*** Public inputs: " + " ".join([str(rounded(pubvals.at(i))) for i in range(pubvals.size())]), file=sys.stderr)
    if do_print: print("*** Verification status:", verifier_strong_IC(keypair.vk, pubvals, proof), file=sys.stderr)
    
    return (keypair.vk, proof, pubvals)


def keygen_only(pk_fname="pysnark_pk",vk_fname="pysnark_vk",do_print=True):
    try:
        pk_fname_file = open(pk_fname,"w")
        vk_fname_file = open(vk_fname,"w")
    except:
        print("File open issue")
        raise RuntimeError("*** File open issue")
        sys.exit()
    if pb.num_constraints()==0:
        # libsnark does not work in this case, add a no-op
        pb.add_r1cs_constraint(libsnark.R1csConstraint(libsnark.LinearCombination(),libsnark.LinearCombination(),libsnark.LinearCombination()))
        
    cs=pb.get_constraint_system_pubs()
    pubvals=pb.primary_input_pubs()
    privvals=pb.auxiliary_input_pubs()
    
    generator          = (libsnark.zkgg_generator if use_groth else libsnark.zk_generator)
    
    keypair=generator(cs)
    keypair.pk.write(pk_fname_file)
    keypair.vk.write(vk_fname_file)
    return (keypair.pk, keypair.vk)

def make_pubvals_file(pk_fname_file,pubvals):
    pubfile=pk_fname_file
    for i in range(pubvals.size()):
       s=str(pubvals.at(i))+"\n"
       pubfile.write(s)
       print(s)
    pubfile.close()

def prove_only(pk_fname="pysnark_pk",proof_log="pysnark_log",pubvals_fname="pysnark_pubvals",do_print=True):
    try:
        proof_log_file = open(proof_log,"w")
        pk_fname_file = open(pk_fname,"r")
        pubvals_file = open(pubvals_fname,"w")
    except:
        print("File open issue")
        raise RuntimeError("*** File open issue")
        sys.exit()

    if pb.num_constraints()==0:
        # libsnark does not work in this case, add a no-op
        pb.add_r1cs_constraint(libsnark.R1csConstraint(libsnark.LinearCombination(),libsnark.LinearCombination(),libsnark.LinearCombination()))
        
    cs=pb.get_constraint_system_pubs()
    pubvals=pb.primary_input_pubs()
    privvals=pb.auxiliary_input_pubs()
    
    prover             = (libsnark.zkgg_prover if use_groth else libsnark.zk_prover)
    write_proof        = (libsnark.zkgg_write_proof if use_groth else libsnark.zk_write_proof)
    read_key           = libsnark.ZKProvingKey_read
    #read_key           = libsnark.zk_read_key
    
    if do_print: print("*** Trying to read pk", file=sys.stderr)
    keypair_pk=read_key(pk_fname_file)
    if not keypair_pk:
            raise RuntimeError("*** Unable to read proving key")
        
    if do_print: 
        print("*** PySNARK: generating proof pysnark_log (" +
              "sat=" + str(pb.is_satisfied()) + 
              ", #io=" + str(pubvals.size()) + 
              ", #witness=" + str(privvals.size()) + 
              ", #constraint=" + str(pb.num_constraints()) +
              ")", file=sys.stderr)
    
    proof=prover(keypair_pk, pubvals, privvals);
    proof.write(proof_log_file)
    proof_log_file.close()
    make_pubvals_file(pubvals_file,pubvals)

    #write_proof(proof, pubvals, proof_log)
    return (proof, pubvals)


def create_pubvals_from_file(pubfile,pb) :
   ff=pubfile.readlines()
   for i in range(len(ff)):
      pubv=libsnark.PbVariable()
      pubv.allocate(pb)
      pb.setpublic(pubv)
      pubval = int(ff[i].strip())
      pb.setval(pubv,pubval)

   pubvals=pb.primary_input_pubs()
   return pubvals


def verify_only(vk_fname="pysnark_vk",pubval_fname="pysnark_pubvals", proof_fname="pysnark_proof", do_print=True):
    try:
        vk_file = open(vk_fname,"r")
        proof_file = open(proof_fname,"r")
        pubfile = open(pubval_fname,"r")
    except:
        print("File open issue")
        raise RuntimeError("*** File open issue")
        sys.exit()
		
    mod = libsnark.get_modulus()
    modd2 = mod//2
    def rounded(val): return val if val<=modd2 else val-mod

    read_vk = libsnark.ZKVerificationKey_read
    read_proof = libsnark.ZKProof_read
    verifier_strong_IC = (libsnark.zkgg_verifier_strong_IC if use_groth else libsnark.zk_verifier_strong_IC)

    
    keypair_vk = read_vk(vk_file)
    vk_file.close()

    pb=libsnark.ProtoboardPub()
    pubvals = create_pubvals_from_file(pubfile,pb)
    pubfile.close()

    proof = read_proof(proof_file)
    proof_file.close()

    if do_print: print("*** Public inputs: " + " ".join([str(rounded(pubvals.at(i))) for i in range(pubvals.size())]), file=sys.stderr)
    verified = verifier_strong_IC(keypair_vk, pubvals, proof)
    if do_print: print("*** Verification status:", verified, file=sys.stderr)
    
    return verified
    
    
