import secrets

#from mpyc.fingroups import EllipticCurve
from petlib.ec import EcGroup, EcPt

group = EcGroup(713)

group_G = group.generator()

ri = group.order().random()
group_H = ri*group_G

setup_file = open("sigma_setup", "w")
print(group_H, file=setup_file)
