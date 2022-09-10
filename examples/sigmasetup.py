import secrets

from mpyc.fingroups import EllipticCurve

group = EllipticCurve('Ed25519')
group_G = group.generator

ri = secrets.randbelow(group.order)
group_H = ri*group_G

setup_file = open("sigma_setup", "w")
print(group_H, file=setup_file)
