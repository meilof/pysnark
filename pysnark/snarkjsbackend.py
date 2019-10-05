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
    
def lcstr(k,v):
    return '    "' + str(k if k>=0 else len(pubvals)-k) + '": "' + str(v%snarkjsp) + '"'
    
def prove():
    wfile = open("witness.json", "w")
    print('[', file=wfile)
    print('  "1",', file=wfile)
    print(',\n'.join(['  "'+str(val)+'"' for val in pubvals+privvals]), file=wfile)
    print(']', file=wfile)
    wfile.close()
          
    cfile = open("circuit.json", "w")
    print('{', file=cfile)
    print('  "signals": [', file=cfile)
    print('    { "names": [ "one" ] },', file=cfile)
    print(',\n'.join(['    { "names": [ "' + str(i+1) + '" ] }' for i in range(len(pubvals)+len(privvals))]), file=cfile)
    print('  ],', file=cfile)
    print('  "constraints": [', file=cfile)
    
    for i in range(len(constraints)):
        print('  [', file=cfile)
        print('    {', file=cfile)
        print(',\n'.join([lcstr(k,v) for (k,v) in constraints[i][0].lc.items()]), file=cfile)
        print('    },', file=cfile)
        print('    {', file=cfile)
        print(',\n'.join([lcstr(k,v) for (k,v) in constraints[i][1].lc.items()]), file=cfile)
        print('    },', file=cfile)
        print('    {', file=cfile)
        print(',\n'.join([lcstr(k,v) for (k,v) in constraints[i][2].lc.items()]), file=cfile)
        print('    }', file=cfile)
        print('  ]' + (',' if i!=len(constraints)-1 else ''), file=cfile)
        
    print('  ],', file=cfile)
    print('  "nPubInputs": 0,', file=cfile)
    print('  "nOutputs": ' + str(len(pubvals)) + ',', file=cfile)
    print('  "nVars": ' + str(len(pubvals)+len(privvals)+1), file=cfile)
    print('}', file=cfile)

    cfile.close()
    
    print("witness.json and circuit.json written; use 'snarkjs setup', 'snarkjs proof', and 'snarkjs verify'", file=sys.stderr)