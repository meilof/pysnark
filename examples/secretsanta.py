# based on https://github.com/lschoe/mpyc/blob/master/demos/secretsanta.py

# * Verifiable secret santa: ook in 1 partij outsourcing setting interessant! Ook vragen over key materiaal... Praktisch: neem aan dat broadcast in de vorm van email bestaat. Aanbieden als web service via aws? Kosten berekenen met vc en vc+mpc. Heeft Amazon pay per use? Alle partijen dragen bij aan randomness seed? 

import functools
import sys

import pysnark.runtime

from pysnark.runtime import PrivVal, LinComb

from pysnark.branching import if_then_else, BranchingValues, _range, _breakif, _endfor
from pysnark.linalg import scalar_mul, vector_sub
from pysnark.hash import ggh_hash
from pysnark.pack import PackRepeat, PackList, PackIntMod, PackBool, PackSeed

def PackPerm(n): return PackList([PackIntMod(i) for i in range(n,1,-1)])

nparties=10
ntries=5

inputformat = PackList([PackIntMod(nparties), PackRepeat(PackPerm(nparties), ntries), PackSeed()])

inputs = []

# generate input of party i in the plain
for i in range(nparties):
    inputi = inputformat.random()
    
    # compute hash in the plain
    print("["+str(i)+"]", ggh_hash(inputformat.pack(inputi)))
    inputs.append(inputi)
    
pperms2 = []

# import into vc
for i in range(nparties):
    packedi = list(map(PrivVal,inputformat.pack(inputs[i])))
    for pi in packedi: pi.assert_bool()
    pperms2.append(inputformat.unpack(packedi,0))
    print("["+str(i)+"]", ggh_hash(packedi).val())
    
def random_permutation(n, cur_rp):
    perm = []
    taken = [0]*n
    for i in range(n,0,-1):
        cur = 0
        for p in range(n):
            #print("cur", p, cur_rp, n-i)
            inp = pperms2[p][1][cur_rp][n-i] if i!=1 else 0
            cur = (cur+inp) % i
           
        hasseen = 0
        for j in range(n):
            #print("do",~hasseen,taken[j],(~hasseen)&taken[j])
            cur += if_then_else((1-hasseen)&taken[j],1,0)
            iscur = cur==j
            hasseen = hasseen|iscur
            if i>1: taken[j] = taken[j]|iscur
        perm.append(cur)
    
    return perm


def random_derangement(n):
    _=BranchingValues()
    
    _.ret=[0]*n
    _.found=0
    
    for cur_rp in _range(ntries):
        _.ret = random_permutation(n, cur_rp)
        isderangement = (functools.reduce(lambda x,y: x*y, [_.ret[i] - i for i in range(n)])!=0)
        _.found=_.found|isderangement
        _breakif(isderangement)
    _endfor()
        
    return (_.found, _.ret)

(found,ret) = random_derangement(nparties)

print("Found permutation", found, ret)

ret2 = [if_then_else(found,(ret[i]+pperms2[i][0]) % nparties,0) for i in range(nparties)]

ppout = PackList([PackBool(), PackRepeat(PackIntMod(nparties), nparties)])

val = LinComb.from_bits(ppout.pack([found,ret2])).val()
print("Output", val)

print(ppout.unpack(PackIntMod(1<<ppout.bitlen()).pack(val),0))

print(ret, found, [if_then_else(found,ret2i,0) for ret2i in ret2])

