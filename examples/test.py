import pysnark.uselibsnark
from pysnark.runtime import PubVal

from pysnark.libsnark import fieldinverse

print(fieldinverse(3))

x=PubVal(3)
x.assert_nonzero()
print(x!=0)

print(abs(PubVal(3)))
print(abs(PubVal(-3)))

print(x<1)
print(x<2)
print(x<3)
print(x<4)
print(x<5)

x.assert_lt(5)
x.assert_lt(4)
##x.assert_lt(3)
##x.assert_lt(2)
##x.assert_lt(1)

print(x==1)
print(x==2)
print(x==3)
print(x==4)
print(x==5)


y=PubVal(4)
z=x*y
print(z)

print("#vars", pysnark.uselibsnark.pb.num_variables())
print("#constraints", pysnark.uselibsnark.pb.num_constraints())
print("sat", pysnark.uselibsnark.pb.is_satisfied())
print(pysnark.libsnark.r1cs_ppzksnark_generator(pysnark.uselibsnark.pb.get_constraint_system()))
