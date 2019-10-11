import libsnark

pb=libsnark.zks_protoboard_pub()

# create variables

inv=libsnark.zks_pb_variable()
inv.allocate(pb)
pb.setpublic(inv)

int=libsnark.zks_pb_variable()
int.allocate(pb)

outv=libsnark.zks_pb_variable()
outv.allocate(pb)
pb.setpublic(outv)

# create constraints

# let int=inv*(2*inv+1)
pb.add_r1cs_constraint(libsnark.zks_r1cs_constraint(libsnark.zks_linear_combination(inv),
                                                libsnark.zks_linear_combination(inv)*2+libsnark.zks_linear_combination(1),
                                                libsnark.zks_linear_combination(int)))
                       
# let out=(int-1)*inv
pb.add_r1cs_constraint(libsnark.zks_r1cs_constraint(libsnark.zks_linear_combination(int)-libsnark.zks_linear_combination(1),
                                                libsnark.zks_linear_combination(inv),
                                                libsnark.zks_linear_combination(outv)))

# create witnesses
pb.setval(inv, 3)
pb.setval(int, 21)
pb.setval(outv, 60)

cs=pb.get_constraint_system_pubs()
pubvals=pb.primary_input_pubs();
privvals=pb.auxiliary_input_pubs();

print("*** Trying to read key")
keypair=libsnark.read_key("ekfile", cs)
if not keypair:
    print("*** No key or computation changed, generating keys...")
    keypair=libsnark.zks_generator(cs)
    libsnark.write_keys(keypair, "vkfile", "ekfile")
    
print("*** Generating proof (" +
      "sat=" + str(pb.is_satisfied()) + 
      ", #io=" + str(pubvals.size()) + 
      ", #witness=" + str(privvals.size()) + 
      ", #constraint=" + str(pb.num_constraints()) +
       ")")
    
proof=libsnark.zks_prover(keypair.pk, pubvals, privvals);
verified=libsnark.zks_verifier_strong_IC(keypair.vk, pubvals, proof);
    
print("*** Public inputs: " + " ".join([str(pubvals.at(i)) for i in range(pubvals.size())]))
print("*** Verification status:", verified)