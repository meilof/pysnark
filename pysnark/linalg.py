# Copyright (C) Meilof Veeningen, 2019

def scalar_mul(a, b):
    return [a*bi for bi in b]

def vector_sub(a, b):
    return [ai-bi for (ai,bi) in zip(a,b)]

def lin_comb(cofs, vals):
    return sum([c*v for (c,v) in zip(cofs, vals)])
