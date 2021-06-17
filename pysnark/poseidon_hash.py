import os
from pysnark import runtime
from pysnark.runtime import LinComb
from pysnark.fixedpoint import LinCombFxp
from pysnark.boolean import LinCombBool
from pysnark.poseidon_constants import poseidon_constants

"""
Implements the Poseidon hash function with 128-bit security and 4-1 reduction
Currently supports the zkinterface and zkifbellman backends
"""

# Load Poseidon parameters
try:
    backend = os.environ["PYSNARK_BACKEND"]
except KeyError:
    backend = "nobackend"

if backend in poseidon_constants:
    constants = poseidon_constants[backend]
else:
    raise NotImplementedError("Poseidon is currently not implemented for this backend")

R_F = constants["R_F"]
R_P = constants["R_P"]
t = constants["t"]
a = constants["a"]
round_constants = constants["round_constants"]
matrix = constants["matrix"]

def matmul(x, y):
    assert(len(x[0]) == len(y))

    result = [[LinComb.ZERO for _ in range(len(y[0]))] for _ in range(len(x))]

    for i in range(len(x)):
        for j in range(len(y[0])):
            for k in range(len(y)):
               result[i][j] += x[i][k] * y[k][j]

    return result

def transpose(inputs):
    result = [[None for _ in range(len(inputs))] for _ in range(len(inputs[0]))]

    for i in range(len(inputs)):
        for j in range(len(inputs[0])):
            result[j][i] = inputs[i][j]

    return result

def permute(sponge):
    """
    Runs the Poseidon permutation
    Costs 400 constraints per permutation call for a power of 5 with a 4-1 reduction
    """

    # First full rounds
    for r in range(R_F // 2):
        # Add round constants
        sponge = [x + y for (x,y) in zip(sponge, round_constants[r])]
        # Full S-box layer
        sponge = [x ** a for x in sponge]
        # Mix layer
        sponge = transpose(matmul(matrix, transpose([sponge])))[0]
        # Reduce internal PySNARK representation of LinComb value modulo prime field
        # Does not affect output circuit
        for x in sponge:
            x.value %= runtime.backend.get_modulus()

    # Partial rounds
    for r in range(R_P):
        # Add round constants
        sponge = [x + y for (x,y) in zip(sponge, round_constants[R_F // 2 + r])]
        # Partial S-box layer
        sponge[0] = sponge[0] ** a
        # Mix layer
        sponge = transpose(matmul(matrix, transpose([sponge])))[0]
        # Reduce internal PySNARK representation of LinComb value modulo prime field
        # Does not affect output circuit
        for x in sponge:
            x.value %= runtime.backend.get_modulus()

    # Final full rounds
    for r in range(R_F // 2):
        # Add round constants
        sponge = [x + y for (x,y) in zip(sponge, round_constants[R_F // 2 + R_P + r])]
        # Full S-box layer
        sponge = [x ** a for x in sponge]
        # Mix layer
        sponge = transpose(matmul(matrix, transpose([sponge])))[0]
        # Reduce internal PySNARK representation of LinComb value modulo prime field
        # Does not affect output circuit
        for x in sponge:
            x.value %= runtime.backend.get_modulus()

    return sponge

def poseidon_hash(inputs):
    """
    Runs the Poseidon hash on a list of LinCombs
    """
    if not isinstance(inputs, list):
        raise RuntimeError("Can only hash lists of LinCombs")
    if not all(map(lambda x : isinstance(x, LinComb) or isinstance(x, LinCombFxp) or isinstance(x, LinCombBool), inputs)):
        raise RuntimeError("Can only hash lists of LinCombs")

    # Convert inputs to LinCombs
    inputs = [x.lc for x in inputs if isinstance(x, LinCombFxp) or isinstance(x, LinCombBool)]

    # Pad inputs
    inputs_per_round = t - 1
    num_pad = inputs_per_round - len(inputs) % inputs_per_round
    num_zeros = num_pad - 1
    inputs = inputs + [LinComb.ONE] + [LinComb.ZERO] * num_zeros
    assert len(inputs) % inputs_per_round == 0

    # Run hash
    sponge = [LinComb.ZERO] * t
    hash_rounds = len(inputs) // inputs_per_round

    for i in range(hash_rounds):
        # Add inputs
        round_inputs = inputs[i * inputs_per_round: (i + 1) * inputs_per_round]
        sponge[1:] = [a + b for (a,b) in zip(sponge[1:], round_inputs)]

        # Run permutation
        sponge = permute(sponge)

    return sponge[1:]