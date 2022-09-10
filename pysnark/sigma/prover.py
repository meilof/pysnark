from threading import get_ident
import gmpy
import secrets

from pysnark.sigma.base import setup, CommittedValue, H, next_curve_point

group_G, group_H, group_order = setup()

proof_file = open("sigma_proof", "w")

def privval(vali):
    ri = secrets.randbelow(group_order)
    gi = vali*group_G + ri*group_H
    print(gi, file=proof_file)
    return CommittedValue(gi, vali, ri)

def pubval(vali):
    return CommittedValue(vali*group_G, vali, 0)

def zero():
    return CommittedValue(0*group_G, 0, 0)
    
def one():
    return CommittedValue(group_G, 1, 0)

def fieldinverse(val):
    return int(gmpy.invert(val, group_order))

def get_modulus():
    return group_order

def add_constraint(v, w, y):
    # proof of correct multiplication
    # see: Lecture Notes Cryptographic Protocols Version 1.7, Berry Schoenmakers,
    # https://www.win.tue.nl/~berry/CryptographicProtocols/, figure S.14 

    assert (v.vi*w.vi-y.vi) % group_order == 0

    u1 = secrets.randbelow(group_order)
    u2 = secrets.randbelow(group_order)
    v1 = secrets.randbelow(group_order)
    v2 = secrets.randbelow(group_order)
    v3 = secrets.randbelow(group_order)

    a1 = u1*group_G + v1*group_H
    a2 = u2*group_G + v2*group_H
    b  = u2*v.gi + v3*group_H

    c  = H(v.gi, w.gi, y.gi, a1, a2, b)

    r1 = (u1 + c*v.vi) % group_order
    r2 = (u2 + c*w.vi) % group_order
    s1 = (v1 + c*v.ri) % group_order
    s2 = (v2 + c*w.ri) % group_order
    s3 = (v3 + c*(y.ri - v.ri*w.vi)) % group_order

    a1 = r1*group_G + s1*group_H - c*v.gi
    a2 = r2*group_G + s2*group_H - c*w.gi
    b  = r2*v.gi + s3*group_H - c*y.gi

    assert H(v.gi, w.gi, y.gi, a1, a2, b) == c

    print(c, r1, r2, s1, s2, s3, sep='\n', file=proof_file)

def prove():
    print("Sigma proof generated succesfully")

def read_commitments():
    from pysnark.runtime import LinComb

    open_file = open("sigma_openings", "r")
    
    ret = {}

    try:
        while True:
            namei = next(open_file).strip()
            gi = next_curve_point(open_file)
            vali = int(next(open_file))
            ri = int(next(open_file))
            ret[namei] = LinComb(vali, CommittedValue(gi, vali, ri))
    except StopIteration:
        pass

    return ret
