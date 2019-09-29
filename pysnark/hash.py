# Adapted from libsnark, developed by SCIPR Lab and contributors (see AUTHORS), MIT licensed.
# Adaptations copyright (C) Meilof Veeningen 2019

import random
import hashlib
import struct
import math

import pysnark.runtime
from pysnark.runtime import LinComb

PRIME = pysnark.runtime.backend.get_modulus()

def bitlength(p):
    #return int(math.ceil(math.log(p, 2)))
    return p.bit_length()

def SHA512_prng(i):
    """Generates nothing-up-my-sleeve random numbers. i-th random number
    is obtained by applying SHA512 to successively (i || 0), (i || 1),
    ... (both i and the counter treated as 64-bit integers) until the
    first of them, when having all but ceil(log(p)) bits cleared, is
    less than p.

    TODO: describe byte order

    """
    mask = 2 ** bitlength(PRIME)
    it = 0
    while True:
        val = int(hashlib.sha512(struct.pack("=QQ", i, it)).digest()[::-1].hex(), 16) % mask
        if val < PRIME:
            return val
        else:
            it += 1

def int_to_bits(i):
    outbits = bin(i)[2:][::-1]
    outbits = outbits + '0' * (bitlength(PRIME) - len(outbits))
    return [int(b) for b in outbits]

def bool_arr(bits):
    return '{%s}' % ','.join(str(b) for b in bits)

def ggh_hash_plain(bits):
    total = 0
    for i, b in enumerate(bits):
        total = (total + b * SHA512_prng(i)) % PRIME
    return total

def ggh_hash_nonplain(bits):
    total = 0
    for i, b in enumerate(bits):
        total = (total + b * SHA512_prng(i))
        total.value = total.value % PRIME
    return total

def rand_bits(count):
    return [random.randint(0, 1) for i in xrange(count)]

def ggh_hash(bits):
    if isinstance(bits[0], LinComb):
        return ggh_hash_nonplain(bits)
    else:
        return ggh_hash_plain(bits)