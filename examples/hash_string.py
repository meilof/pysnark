# compute knowledge of a fixed-length string being a preimage of a public constant hash

from pysnark.runtime import PrivVal, snark, PubVal
from pysnark.hash import ggh_hash
from pysnark.pack import PackIntMod

import random
random.seed()

def str_to_arr(strn, leng):
	if len(strn)>leng: raise ValueError("String too long")		
	return [ord(strn[i]) if i<len(strn) else 0 for i in range(leng)]

def arr_to_str(arr):
	return "".join([chr(x) for x in arr])

class PackString:
	def __init__(self, len): 
		self.len = len
		self.pim = PackIntMod(0x10FFFF)
		
	def random(self):
		return "".join([chr(self.pim.random()) for _ in range(self.len)])
	
	def bitlen(self):
		return self.pim.bitlen()*self.len

	def pack(self, val):
		if isinstance(val[0], str): val = str_to_arr(val, self.len)
		if len(val)!=self.len: raise ValueError("Input string has incorrect length")
		return [b for ix in range(self.len) for b in self.pim.pack(val[ix])]
		
	def unpack(self, bits, pos): 
		ups = [self.pim.unpack(bits, pos+i*self.pim.bitlen()) for i in range(self.len)]
		if isinstance(ups[0], int): return arr_to_str(ups) 
		return ups

	
# plain computation of hash
packer = PackString(32)
packed = packer.pack("Hello, World")
print(ggh_hash(packed))
print(packer.unpack(packed, 0))
# prints 7428734505000537051458020718527270693901292844728698721298764680875509535006

witness = [PrivVal(x) for x in str_to_arr("Hello, World", 32)]
hashed = ggh_hash(packer.pack(witness))
print(hashed.val())
# to enforce that the hash is equal to a hardcoded hash
hashed.assert_eq(7428734505000537051458020718527270693901292844728698721298764680875509535006)
# or, to make it a public input instead of a hardcoded constant: 
hashed.assert_eq(PubVal(7428734505000537051458020718527270693901292844728698721298764680875509535006))

