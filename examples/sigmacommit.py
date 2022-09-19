import secrets
import sys

from pysnark.sigma.base import setup

group_G, group_H, group_order = setup()

commit_file = open("sigma_commitments", "w")
open_file = open("sigma_openings", "w")

for arg in sys.argv[1:]:
    namei,vali = arg.split(":")
    vali = int(vali)
    ri = group_order.random()
    gi = (vali*group_G)+(ri*group_H)
    print(namei, gi, sep='\n', file=commit_file)
    print(namei, gi, vali, ri, sep='\n', file=open_file)
