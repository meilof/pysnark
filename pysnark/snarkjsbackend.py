import sys

import pysnark.gmpy

snarkjsp=21888242871839275222246405745257275088548364400416034343698204186575808495617

class LinearCombination:
    def __init__(self, lc): self.lc = lc
    def __add__(self, other):
        lc = dict()
        for a in self.lc:
            if a in other.lc:
                lc[a] = self.lc[a] + other.lc[a]
            else:
                lc[a] = self.lc[a]
        for b in other.lc:
            if not b in self.lc:
                lc[b] = other.lc[b]
        return LinearCombination(lc)
    
    def __sub__(self, other):
        return self+(-other)
    
    def __mul__(self, other):
        return LinearCombination({key:value*other for (key,value) in self.lc.items()})

    def __neg__(self):
        return self*-1

privvals = []
    
def privval(val):
    privvals.append(val)
    return LinearCombination({-len(privvals):1})

pubvals = []

def pubval(val):
    pubvals.append(val)
    return LinearCombination({len(pubvals):1})

def zero():
    return LinearCombination({})
    
def one():
    return LinearCombination({0:1})

def fieldinverse(val):
    return int(gmpy.invert(val, snarkjsp))

def get_modulus():
    return snarkjsp

constraints = []
def add_constraint(v, w, y):
    constraints.append([v,w,y])
    
def prove():
    wfile = open("witness.wtns", "wb")

    def wwriteval(val, len):
        wfile.write(bytes([(val>>(i*8)) & 255 for i in range(len)]))

    # 4 bytes: "wtns"
    wfile.write(bytes("wtns", encoding="Latin-1"))

    # 4 bytes: 02000000 (versienummer)
    wwriteval(2, 4)

    # 4 bytes: 02000000 (aantal secties)
    wwriteval(2, 4)

    # 4 bytes: 01000000 (sectie #1)
    wwriteval(1, 4)

    # 8 bytes: 28000000 000000 (lengte sectie #1: 40 bytes)
    wwriteval(40, 8)

    # 4 bytes: 20000000 (lengte modulus: 32 bytes)
    wwriteval(32, 4)

    # 32 bytes: 010000F0 93F5E143 9170B979 48E83328 5D588181 B64550B8 29A031E1 724E6430 (modulus)
    wwriteval(snarkjsp, 32)

    # 4 bytes: 06000000 (aantal getallen in witness)
    wwriteval(len(pubvals)+len(privvals)+1, 4)

    # 4 bytes: 02000000 (sectie #2)
    wwriteval(2, 4)

    # 8 bytes: C0000000 00000000 (lengte sectie #2: 192=32*6)
    wwriteval((len(pubvals)+len(privvals)+1)*32, 8)

    # 32 bytes: 01000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 (eerste witness)
    wwriteval(1, 32)
    for val in pubvals: wwriteval(val, 32)
    for val in privvals: wwriteval(val, 32)

    wfile.close()

    cfile = open("circuit.r1cs", "wb")

    def cwriteval(val, len):
        cfile.write(bytes([(val>>(i*8)) & 255 for i in range(len)]))

    # 4 bytes: "r1cs"
    cfile.write(bytes("r1cs", encoding="Latin-1"))

    # 01000000 versienummer
    cwriteval(1, 4)

    # 03000000 aantal secties
    cwriteval(3, 4)

    # 01000000 sectie 1
    cwriteval(1, 4)

    # 40000000 00000000 lengte 64
    cwriteval(64, 8)

    # 20000000 lengte modulus=32 bytes
    cwriteval(32, 4)

    # 010000F0 93F5E143 9170B979 48E83328 5D588181 B64550B8 29A031E1 724E6430 modulus
    cwriteval(snarkjsp, 32)

    # 06000000 nvars=6
    cwriteval(len(privvals)+len(pubvals)+1, 4)

    # 01000000 noutputs=1
    cwriteval(len(pubvals), 4)

    # 00000000 npubinputs=0
    cwriteval(0, 4)

    # 02000000 nprivinputs=2
    cwriteval(0, 4)

    # 07000000 00000000 nlabels=7
    cwriteval(0, 8) # ???

    # 03000000 nconstraints=3
    cwriteval(len(constraints), 4)

    # 02000000 sectie 2
    cwriteval(2, 4)

    # D4010000 00000000 lengte 468
    nlcs = sum([len(c[0].lc)+len(c[1].lc)+len(c[2].lc) for c in constraints])
    cwriteval(12*len(constraints)+36*nlcs, 8)  # ???

    # c1:v
    # 01000000 ncoeffs
    # 02000000 var
    # 000000F0 93F5E143 9170B979 48E83328 5D588181 B64550B8 29A031E1 724E6430 val
    # c1:w
    # 01000000 ncoeffs
    # 02000000
    # 01000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 val
    # c1:z
    # 02000000 ncoeffs
    # 03000000 var
    # 01000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 val
    # 04000000 var
    # 000000F0 93F5E143 9170B979 48E83328 5D588181 B64550B8 29A031E1 724E6430 val

    def writefac(k,v):
        cwriteval(k if k >= 0 else len(pubvals) - k, 4)
        cwriteval(v % snarkjsp, 32)

    for c in constraints:
        cwriteval(len(c[0].lc), 4)
        for (k,v) in c[0].lc.items(): writefac(k, v)
        cwriteval(len(c[1].lc), 4)
        for (k,v) in c[1].lc.items(): writefac(k, v)
        cwriteval(len(c[2].lc), 4)
        for (k,v) in c[2].lc.items(): writefac(k, v)


    # 03000000 sectie 3
    cwriteval(3, 4)

    # 30000000 00000000 lengte 48
    cwriteval(8*(len(privvals)+len(pubvals)+1), 8)

    for i in range(len(privvals)+len(pubvals)+1):
        # 00000000 00000000 index 0
        cwriteval(0, 8)

    cfile.close()

    print("snarkjs witness.wtns and circuit.r1cs written; see readme", file=sys.stderr)