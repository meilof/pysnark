# Copytight (C) Meilof Veeningen, 2019

import os
import sys

# load backend

if "pysnark.qaptools.backend" in sys.modules:
    backend=sys.modules["pysnark.qaptools.backend"]
elif "pysnark.nobackend" in sys.modules:
    backend=sys.modules["pysnark.nobackend"]
elif "pysnark.libsnark.backend" in sys.modules:
    backend=sys.modules["pysnark.libsnark.backend"]
elif "PYSNARK_BACKEND" in os.environ:
    if os.environ["PYSNARK_BACKEND"]=="qaptools":
        import pysnark.qaptools.backend
        backend=pysnark.qaptools.backend
    elif os.environ["PYSNARK_BACKEND"]=="libsnark":
        import pysnark.libsnark.backend
        backend=pysnark.libsnark.backend
    else:
        if os.environ["PYSNARK_BACKEND"]!="none":
            print("*** PySNARK: unknown backend in environment variables: " + os.environ["PYSNARK_BACKEND"])
        import pysnark.nobackend
        backend=pysnark.nobackend
else:
    try:
        import pysnark.libsnark.backend
        backend=pysnark.libsnark.backend
    except:
        try:
            import pysnark.qaptools.backend
            backend=pysnark.qaptools.backend
        except:
            import pysnark.nobackend
            backend=pysnark.nobackend
            print("*** PySNARK: no backend avaiable, not making proofs", file=sys.stderr)
            

"""
Operating principles:
 - if wrong type of value is given as argument, raise ValueError or
   NotImplemented
 - if wrong values are given:
     - if ignore_errors is given, proceed and generate the same constraints
       as normal (use add_constraint_unsafe for constraints that will still
       always hold and add_constraint otherwise)
     - otherwise, raise ValueError or AssertionError
"""
ignore_errors=False

""" Bitlength for bitwise operations. Values are signed values between -2^(bitlength-1) and 2^(bitlength-1) """
bitlength=16

def is_base_value(obj): return isinstance(obj, int)

def assert_base_value(obj):
    if not is_base_value(obj):
        raise TypeError("value " + obj + " has unsupported type " + type(obj))

num_constraints = 0
        
def add_constraint_unsafe(v, w, y):
    global num_constraints
    num_constraints += 1
    backend.add_constraint(v.lc, w.lc, y.lc)
    
def benchmark(callback = lambda x: print("*** Num constraints:", x)):
    def _benchmark(fn):
        def __benchmark(*args, **kwargs):
            prev_num_constraints = num_constraints
            ret = fn(*args, **kwargs)
            callback(num_constraints - prev_num_constraints)
            return ret
        return __benchmark
    return _benchmark

"""
If set, all constraints added via add_constraint will be guarded by this guard,
meaning that if guard.value==1, they should be satfiesfied and if guard.value==0,
a dummy value will be added to satisfy them
"""
guard = None

def add_guard(cond):
    global guard, ignore_errors

    _orig_guard = guard
    _orig_ignore_errors = ignore_errors
    _orig_ONE = LinComb.ONE
    
    guard = cond if guard is None else cond&guard
    ignore_errors = ignore_errors or (cond.value==0)
    LinComb.ONE = guard
    
    return (_orig_guard,_orig_ignore_errors,_orig_ONE)

def restore_guard(bak):
    global guard, ignore_errors
    
    (_orig_guard,_orig_ignore_errors,_orig_ONE)=bak
    guard = _orig_guard
    ignore_errors = _orig_ignore_errors
    LinComb.ONE = _orig_ONE    


def guarded(cond):
    def _guarded(fn):
        def __guarded(*args, **kwargs):
            bak = enable_guard(cond)
            
            try:
                ret = fn(*args, **kwargs)
                restore_guard(bak)
            except:
                restore_guard(bak)
                raise
        
            return ret
        
        return __guarded
    return _guarded

def is_dummy():
    return (guard is not None and guard.value==0)

""" Add constraint v*w=y to the constraint system, and update running computation hash. """
def add_constraint(v,w,y):
    if not guard is None:
        dummy = PrivVal(v.value*w.value-y.value)
        add_constraint_unsafe(v,w,y+dummy)
        add_constraint_unsafe(guard,dummy,LinComb.ZERO)
    else:
        if v.value*w.value!=y.value:
            # note that we do the check over the integers
            if ignore_errors: raise ValueError("Constraint did not hold")
            
        add_constraint_unsafe(v,w,y)

class LinComb:
    def __init__(self, value, lc):
        self.value = value
        self.lc = lc   
        
    def val(self):
        """ Creates a SNARK output for the current output and return its value """
        (self-PubVal(self.value)).assert_zero()     
        return self.value
    
    def __repr__(self):
        return "{" + str(self.value) + "}"
    
    def __deepcopy__(self, memodict):
        return self
    
    # self<other, so other-self>0, so other-self-1>=0
    def __lt__(self, other): return (other-self-1).check_positive()
    def assert_lt(self, other): (other-self-1).assert_positive()
        
    # self<=other, so other-self>=0
    def __le__(self, other): return (other-self).check_positive()
    def assert_le(self, other): (other-self).assert_positive()
    
    def __eq__(self, other): return (self-other).check_zero()
    def assert_eq(self, other): (self-other).assert_zero()
        
    def __ne__(self, other): return 1-(self==other)
    def assert_ne(self, other): (self-other).assert_nonzero()
        
    # self>other, so self-other>0, so self-other-1>=0
    def __gt__(self, other): return (self-other-1).check_positive()
    def assert_gt(self, other): (self-other-1).assert_positive()
        
    # self>=other, so self-other>=0
    def __ge__(self, other): return (self-other).check_positive()
    def assert_ge(self, other): (self-other).assert_positive()
        
    def __bool__(self):
        raise NotImplementedError("Should not run bool() on a LinComb")
        
    def __add__(self, other):
        if isinstance(other, LinComb):
            return LinComb(self.value+other.value, self.lc+other.lc)
        elif is_base_value(other):
            return self + other*LinComb.ONE
        else:
            return NotImplemented
        
    def __sub__(self, other):
        return self+(-other)
    
    def __mul__(self, other):
        if isinstance(other, LinComb):
            retval = PrivVal(self.value*other.value)
            add_constraint_unsafe(self, other, retval)
            return retval
        elif is_base_value(other):
            return LinComb(self.value*other, self.lc*other)
        else:
            return NotImplemented
                    
    def __matmul__(self, other): return NotImplemented
    
    def __truediv__(self, other): 
        """ Proper division """
        if isinstance(other, LinComb):
            if (not is_dummy()) and self.value % other.value == 0:
                res = PrivVal(self.value/other.value)
            elif ignore_errors:
                res = PrivVal(0)
            else:
                raise ValueError(str(self.value) + " is not properly divisible by " + str(other.value))
            add_constraint(other, res, self)
            return res
        elif is_base_value(other):
            if self.value % other == 0:
                raise ValueError(str(self.value) + " is not properly divisible by " + str(other))
            return LinComb(self.value/other, self.lc*backend.fieldinverse(other))
        else:
            return NotImplemented
         
    def __floordiv__(self, other):
        """ Division with rounding """
        return self.__divmod__(other)[0]

    def __mod__(self, other):
        if other&(other-1)==0:
            # this is faster for powers of two
            return LinComb.from_bits(self.to_bits()[:other.bit_length()-1])
        
        return self.__divmod__(other)[1]
        
    def __divmod__(self, divisor):
        """ Division by public value """
        
        if not is_base_value(divisor): return NotImplemented
        
        if divisor==0: raise ValueError("division by zero")
        
        quo = PrivVal(self.value//divisor)
        rem = PrivVal(self.value-quo.value*divisor)
 
        rem.assert_positive(divisor.bit_length())
        if divisor&(divisor-1)!=0: rem.assert_lt(divisor) # not needed for powers of two
        quo.assert_positive()
        (self-divisor*quo-rem).assert_zero()
        
        return (quo,rem)
    
    def __pow__(self, other, mod=None):
        """ Exponentiation with public integral power p>=0 """
        if mod!=None: raise ValueError("cannot provide modulus")
        if not is_base_value(other): return NotImplemented
        if other<0: raise ValueError("exponent cannot be negative", other)
        if other==0: return LinComb.ONE
        if other==1: return self
        return self*pow(self, other-1)
    
    def __lshift__(self, other):
        """ Left-shift with public value """
        # TODO: extend to secret offset?
        if not is_base_ovalue(other): return NotImplemented
        return self*(1<<other)
    
    def __rshift__(self, other):
        """ Right-shift with public value """
        # TODO: extend to secret offset?
        if not is_base_ovalue(other): return NotImplemented
        return LinComb.from_bits(self.to_bits[other:])
    
    def _check_both_bits(self, other):
        if ignore_errors: return
        
        if self.value !=0 and self.value!=1: raise ValueError("not a bit: " + str(self.value))
            
        if isinstance(other, LinComb) and (other.value==0 or other.value==1): return
        if is_base_value(other) and (other==0 or other==1): return
        raise ValueError("not a bit: " + str(other))
    
    def __and__(self, other):
        """ Bitwise and &. Cost: 1 constraint """
        self._check_both_bits(other)
        return self * other

    def __xor__(self, other):
        """Bitwise exclusive-or ^. Cost: 1 constraint """
        self._check_both_bits(other)
        return self + other - 2 * self * other

    def __or__(self, other):
        """Bitwise or |. Cost: 1 constraint """
        self._check_both_bits(other)
        return self + other - self * other

    __radd__ = __add__

    def __rsub__(self, other):
        return other+(-self)
    
    __rmul__ = __mul__
    
    def __rmatmul__(self, other): return NotImplemented

    def __rtruediv__(self, other):
        """ Proper division by LinComb """
        if not is_base_value(other): return NotImplemented
        
        if (not is_dummy()) and other % self.value == 0:
            res = PrivVal(other/self.value)
        elif ignore_errors:
            res = PrivVal(0)
        else:
            raise ValueError(str(other.value) + " is not properly divisible by " + str(self.value))
        
        add_constraint(self, res, other*LinComb.ONE)
        return res
        
    def __rfloordiv__(self, other): return NotImplemented
    def __rmod__(self, other): return NotImplemented
    def __rdivmod__(self, other): return NotImplemented
    def __rpow__(self, other): return NotImplemented
    def __rlshift__(self, other): return NotImplemented
    def __rrshift__(self, other): return NotImplemented

    __rand__ = __and__
    __rxor__ = __xor__
    __ror__ = __or__

    def __neg__(self):
        return LinComb(-self.value, -self.lc)
    
    def __pos__(self):
        return self
    
    def __abs__(self):
        from .branching import if_then_else
        return if_then_else(self>=0, self, -self)

    def __invert__(self):
        # we do not want to do ~1=0 and ~0=1 since this is also not true for native ints
        raise NotImplementedError("Operator ~ not supported. For binary not, use 1-x")
        
    def __complex__(self): return NotImplemented
    def __int__(self): raise NotImplementedError("Should not run int() on LinComb")
    def __float__(self): return NotImplemented
    
    def __round__(self, ndigits=None): return NotImplemented
    def __trunc__(self): return NotImplemented
    def __floor__(self): return NotImplemented
    def __ceil__(self): return NotImplemented

    def assert_bool(self):
        add_constraint(self, 1-self, LinComb.ZERO)

    def assert_bool_unsafe(self):
        add_constraint_unsafe(self, LinComb.ONE_SAFE-self, LinComb.ZERO)
        
    def to_bits(self, bits=None):
        if bits is None: bits=bitlength
            
        if (not ignore_errors) and (self.value<0 or self.value.bit_length()>bits):
            raise ValueError("value " + str(self.value) + " is not a " + str(bits) + "-bit positive integer")
            
        bits = [PrivVal((self.value&(1<<ix))>>ix) for ix in range(bits)]
        for bit in bits: bit.assert_bool_unsafe()
            
        (self-LinComb.from_bits(bits)).assert_zero()
        
        return bits
        
    @classmethod
    def from_bits(cls, bits):
        return sum([biti*(1<<i) for (i,biti) in enumerate(bits)])
        
    """
    Given a value in [-1<<bitlength,1>>bitlength], check if it is positive.
    Note that this works on (bitlength+1)-length values so it works for
    __lt__, etc on bitlength-length values
    """
    def check_positive(self, bits=None):
        if bits is None: bits=bitlength
            
        if (not is_dummy()) and self.value.bit_length()<=bits:
            ret = PrivVal(1 if self.value>=0 else 0)
            abs = self.value if self.value>=0 else -self.value
            bits = [PrivVal((abs&(1<<ix))>>ix) for ix in range(bits)]
        elif ignore_errors:
            ret = PrivVal(0)
            bits = [PrivVal(0) for _ in range(bits)]
        else:
            raise ValueError("value " + str(self.value) + " is not a " + str(bits) + "-bit integer")
            
        for bit in bits: bit.assert_bool_unsafe()
        
        # if ret==1, then requires that 2*self=self+sum, so sum=self
        # if ret==0, this requires that 0=self+sum, so sum=-self
        add_constraint(2*ret, self, self+LinComb.from_bits(bits))
        
        return ret
            
    def assert_positive(self, bits=None):
        if bits is None: bits=bitlength
        self.to_bits(bits)
        
    def check_zero(self):
        ret = PrivVal(1 if self.value==0 else 0)
        
        wit = PrivVal(backend.fieldinverse(self.value+ret.value))  # add ret.value so always nonzero
        
        # Trick from Pinocchio paper: if self is zero then ret=1 by first eq,
        # if self is nonzero then ret=0 by second eq
        add_constraint_unsafe(self, wit, LinComb.ONE_SAFE-ret)
        add_constraint_unsafe(self, ret, LinComb.ZERO)
        
        return ret
    
    def assert_zero(self):
        if (not ignore_errors) and self.value!=0:
            raise ValueError("Value " + str(self.value) + " is not zero")
            
        add_constraint(LinComb.ZERO, LinComb.ZERO, self)        
            
    def assert_nonzero(self):
        if (not is_dummy()) and self.value!=0:
            wit = PrivVal(backend.fieldinverse(self.value))    
        elif ignore_errors:
            wit = PrivVal(0)
        else:
            raise ValueError("Value " + str(self.value) + " is not zero")
        
        add_constraint(self, wit, LinComb.ONE)
    
LinComb.ZERO = LinComb(0, backend.zero())
LinComb.ONE = LinComb(1, backend.one())
LinComb.ONE_SAFE = LinComb.ONE

def PubVal(val):
    return LinComb(val, backend.pubval(val))

def PrivVal(val):
    return LinComb(val, backend.privval(val))

def for_each_in(cls, f, struct):
    """ Recursively traversing all lists and tuples in struct, apply f to each
        element that is an instance of cls. Returns structure with f applied. """
    if isinstance(struct, list):
        return list(map(lambda x: for_each_in(cls, f, x), struct))
    elif isinstance(struct, tuple):
        return tuple(map(lambda x: for_each_in(cls, f, x), struct))
    else:
        if isinstance(struct, cls):
            return f(struct)
        else:
            return struct

"""
Turns the given function into a SNARK. Input and outputs to the function are
converted to public SNARK inputs (via PubVal). Input/output conversion is also
performed over lists and tuples, but not over more complex objects.

Can be used as a decorator, e.g., 

>>> pysnark.runtime.snark(lambda x: x*x*x)(3)
9
"""
def snark(fn):
    def snark__(*args, **kwargs):
        if kwargs: raise ValueError("@snark-decorated functions cannot have keyword arguments")

        argscopy = for_each_in(int, lambda x: PubVal(x), args)
        ret = fn(*argscopy, **kwargs)
        retcopy = for_each_in(LinComb, lambda x: x.val(), ret)

        return retcopy
        
    return snark__

import atexit
from .atexitmaybe import maybe
atexit.register(maybe(backend.prove))
