import functools
import random
random.seed()

from pysnark.runtime import LinComb

class PackBool:
    def random(self): return random.randrange(0,2)
    def bitlen(self): return 1
    def pack(self, val): return [val] if isinstance(val,LinComb) else [int(bool(val))]
    def unpack(self, bits, pos): return bits[pos]

class PackIntMod:
    mod = None
    
    def __init__(self, mod):
        self.mod = mod
        
    def random(self):
        return random.randrange(0,self.mod)
        
    def bitlen(self):
        return (self.mod-1).bit_length()
    
    def pack(self, val):
        if isinstance(val,LinComb):
            # lincomb in: no boundary checking
            return val.to_bits((self.mod-1).bit_length())
        else:
            # val in: boundary checking
            if val<0 or val>=self.mod:
                raise ValueError("Value out of bounds: 0<=" + str(val) + "<" + str(self.mod) + " not true")
            return [(val & (1 << i)) >> i for i in range((self.mod-1).bit_length())]
        
    def unpack(self, bits, pos):
        if isinstance(bits[pos],LinComb):
            # lincomb in: boundary checking
            ret = LinComb.from_bits(bits[pos:pos+self.bitlen()])
            ret.assert_lt(self.mod)
            return ret
        else:
            return sum([(1<<ix)*v for (ix,v) in enumerate(bits[pos:pos+self.bitlen()])])

class PackList:
    lst = None
    
    def __init__(self, lst):
        self.lst = lst
        
    def random(self):
        return [i.random() for i in self.lst]
    
    def bitlen(self):
        return sum([i.bitlen() for i in self.lst])
    
    def pack(self, val):
        return functools.reduce(lambda x,y: x+y, [i.pack(j) for (i,j) in zip(self.lst, val)])
        
    def unpack(self, bits, pos):
        def unpacknext(i):
            nonlocal pos
            ret = i.unpack(bits, pos)
            pos += i.bitlen()
            return ret
        
        return list(map(unpacknext, self.lst))

class PackRepeat:
    packer = None
    times = None
    
    def __init__(self, packer, times):
        self.packer = packer
        self.times = times
        
    def random(self):
        return [self.packer.random() for _ in range(self.times)]
    
    def bitlen(self):
        return self.packer.bitlen()*self.times
    
    def pack(self, val):
        return functools.reduce(lambda x,y: x+y, map(self.packer.pack, val))
        
    def unpack(self, bits, pos):
        bl = self.packer.bitlen()
        return [self.packer.unpack(bits, pos+i*bl) for i in range(self.times)]
    
def PackSeed(bits = 40): return PackRepeat(PackBool(), bits)

