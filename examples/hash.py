# compute knowledge of a bitstring being a preimage of a public constant hash

from pysnark.runtime import PrivVal, snark, PubVal, LinComb
from pysnark.hash import ggh_hash
	
# plain computation of hash
bitstring = [1,0,1,1,1,0,1,0,1,1,1,0,1]
print(ggh_hash(bitstring))
# prints 3815100955245901773194254220410253439371965309251566846530536701111841134788

# now define preimage as a witness
witness = [PrivVal(x) for x in [1,0,1,1,1,0,1,0,1,1,1,0,1]]
# prove that the preimafe is actually a bit string
for w in witness: w.assert_bool()
# compute hash as a verifiable computation
hashed = ggh_hash(witness)

hashed.assert_eq(3815100955245901773194254220410253439371965309251566846530536701111841134788)
# enforce that the hash is equal to intended hash, public input to computation
hashed.assert_eq(PubVal(3815100955245901773194254220410253439371965309251566846530536701111841134788))
# output computed hash as a public output of the verifiable computation
print(hashed.val())
