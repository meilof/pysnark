from threading import get_ident
import gmpy
import secrets

from pysnark.sigma.base import setup, H, next_curve_point

group_G, group_H, group_order = setup()

proof_file = open("sigma_proof", "r")

def privval(vali):
    return next_curve_point(proof_file)

def pubval(vali):
    return vali*group_G

def zero():
    return 0*group_G
    
def one():
    return group_G

def fieldinverse(val):
    return int(gmpy.invert(val, group_order))

def get_modulus():
    return group_order

def add_constraint(v, w, y):
    # proof of correct multiplication
    # see: Lecture Notes Cryptographic Protocols Version 1.7, Berry Schoenmakers,
    # https://www.win.tue.nl/~berry/CryptographicProtocols/, figure S.14 

    c = int(next(proof_file))
    r1 = int(next(proof_file))
    r2 = int(next(proof_file))
    s1 = int(next(proof_file))
    s2 = int(next(proof_file))
    s3 = int(next(proof_file))

    a1 = r1*group_G + s1*group_H - c*v
    a2 = r2*group_G + s2*group_H - c*w
    b  = r2*v + s3*group_H - c*y

    assert H(v, w, y, a1, a2, b) == c


def prove():
    print("Sigma proof verified succesfully")

def read_commitments():
    from pysnark.runtime import LinComb, ignore_errors
    ignore_errors(True)

    open_file = open("sigma_commitments", "r")
    
    ret = {}

    try:
        while True:
            namei = next(open_file).strip()
            gi = next_curve_point(open_file)
            ret[namei] = LinComb(0, gi)
    except StopIteration:
        pass

    return ret

