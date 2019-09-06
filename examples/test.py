import pysnark.libsnark
import pysnark.runtime
from pysnark.runtime import PubVal

x=PubVal(3)
y=PubVal(4)
z=x*y

print(pysnark.runtime.pb)
print(pysnark.runtime.pb.num_variables())

print(pysnark.libsnark.r1cs_ppzksnark_generator(pysnark.runtime.pb.get_constraint_system()))
