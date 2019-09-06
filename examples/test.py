import pysnark.uselibsnark
from pysnark.runtime import PubVal

x=PubVal(3)
y=PubVal(4)
z=x*y

print(pysnark.uselibsnark.pb)
print(pysnark.uselibsnark.pb.num_variables())

print(pysnark.libsnark.r1cs_ppzksnark_generator(pysnark.uselibsnark.pb.get_constraint_system()))
