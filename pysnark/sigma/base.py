import sys

from hashlib import sha1, sha224, sha256, sha384, sha512
from mpyc.fingroups import EllipticCurve, EllipticCurvePoint

group = EllipticCurve('Ed25519')

# also allow post-multiplication by scalars, since pysnark does this
type(group.generator).__mul__ = type(group.generator).__rmul__

def next_curve_point(file):
    """ Read curve point from file """
    line = next(file).split()
    xi = int(line[0][1:-1])
    yi = int(line[1][:-1])
    return type(group.generator)((xi,yi))

def setup():
    """ Read Pedersen setup: returning group elements g, h and group order """
    group_G = group.generator

    try:
        setup_file = open("sigma_setup", "r")
        group_H = next_curve_point(file=setup_file)
    except BaseException as err:
        print("*** Could not read sigma_setup, run sigmasetup.py first")
        sys.exit(1)

    return group_G, group_H, group.order

# Adapted from https://github.com/lschoe/mpyc/blob/master/demos/dsa.py
# Note that this works for int inputs as well
def to_bytes(a):
    """Map group element a to fixed-length byte string."""
    if isinstance(a, EllipticCurvePoint):  # cf. ECDSA
        z = int(a.normalize().x)           # x-coordinate of point a on elliptic curve
    else:           # cf. DSA
        z = int(a)  # Schnorr group element a
    N = (a.field.order.bit_length() + 7) // 8
    return z.to_bytes(length=N, byteorder='big')

# Adapted from https://github.com/lschoe/mpyc/blob/master/demos/dsa.py
def H(*vals):
    """Hash a and M using a SHA-2 hash function with sufficiently large output length."""
    N = (group.order.bit_length() + 7) // 8  # byte length
    N_sha = ((20, sha1), (28, sha224), (32, sha256), (48, sha384))
    sha = next((sha for _, sha in N_sha if _ >= N), sha512)

    M = b''.join(map(to_bytes, vals))

    c = int.from_bytes(sha(M).digest()[:N], byteorder='big')
    return c

class CommittedValue:
    """ Represents a Pedersen-committed value of with known opening """
    def __init__(self, gi, vi, ri):
        self.gi = gi
        self.vi = vi
        self.ri = ri

    def __add__(self, other):
        return CommittedValue(self.gi+other.gi, 
                              (self.vi+other.vi) % group.order,
                              (self.ri+other.ri) % group.order)
    
    def __sub__(self, other):
        return self+(-other)
    
    def __mul__(self, other):
        return CommittedValue(other*self.gi, 
                              (other*self.vi) % group.order,
                              (other*self.ri) % group.order)

    __rmul__ = __mul__

    def __neg__(self):
        return CommittedValue(-self.gi, 
                              group.order-self.vi,
                              group.order-self.ri)
