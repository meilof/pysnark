import json
import sys

import pysnark.libsnark.backend as lsbackend
import pysnark.runtime

from pysnark.runtime import snark, PrivVal
from pysnark.libsnark.tosnarkjs import SnarkjsEncoder

pysnark.runtime.autoprove = False

@snark
def cube(x):
    return x*x*x

print("The cube of", sys.argv[1], "is", cube(int(sys.argv[1])))

(vk, proof, pubvals) = lsbackend.prove(do_keygen=False, do_write=False, do_print=True)

print(json.dumps(vk, cls=SnarkjsEncoder))
print(json.dumps(proof, cls=SnarkjsEncoder))
print(json.dumps(pubvals, cls=SnarkjsEncoder))
