# Copyright (C) Meilof Veeningen, 2019

import importlib
import os
import sys

backend = None
backend_name = None

backends = [
    ["libsnark",    "pysnark.libsnark.backend"],
    ["libsnarkgg",  "pysnark.libsnark.backendgg"],
    ["qaptools",    "pysnark.qaptools.backend"],
    ["snarkjs",     "pysnark.snarkjsbackend"],
    ["zkinterface", "pysnark.zkinterface.backend"],
    ["zkifbellman", "pysnark.zkinterface.backendbellman"],
    ["zkifbulletproofs", "pysnark.zkinterface.backendbulletproofs"],	
    ["nobackend",   "pysnark.nobackend"]
]

for mod in backends:
    if mod[1] in sys.modules:
        backend_name = mod[0]
        backend = sys.modules[mod[1]]
        break

if backend is None and "PYSNARK_BACKEND" in os.environ:
    for mod in backends:
        if os.environ["PYSNARK_BACKEND"]==mod[0]:
            backend_name = mod[0]
            backend = importlib.import_module(mod[1])
    if backend is None:
        print("*** PySNARK: unknown backend in environment variables: " + os.environ["PYSNARK_BACKEND"])

if backend is None:
    try:
        get_ipython()
        import pysnark.nobackend
        backend_name = "nobackend"
        backend = pysnark.nobackend
    except:
        for mod in backends:
            try:
                backend_name = mod[0]
                backend = importlib.import_module(mod[1])
                break
            except Exception as e:
                print("*** Error loading backend " + str(mod[1]) + ":", e)

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
_ignore_errors=False

def ignore_errors(val = None):
    global _ignore_errors
    if val is not None:
        _ignore_errors = val
    return _ignore_errors

""" Bitlength for bitwise operations. Values are signed values between -2^(bitlength-1) and 2^(bitlength-1) """
bitlength=16

def is_base_value(obj): return isinstance(obj, int)

def assert_base_value(obj, err=None):
    if not is_base_value(obj):
        raise TypeError(err if err is not None else "value " + obj + " has unsupported type " + type(obj))

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
Should be None or a LinComb with value 0 or 1
If set, all constraints added via add_constraint will be guarded by this guard,
meaning that if guard.value==1, they should be satfiesfied and if guard.value==0,
a dummy value will be added to satisfy them
"""
guard = None

def add_guard(cond):
    global guard, _ignore_errors

    _orig_guard = guard
    _orig_ignore_errors = _ignore_errors
    _orig_ONE = LinComb.ONE
    
    if isinstance(cond,LinComb):
        if not ignore_errors() and (cond.value!=0 and cond.value!=1):
            raise RuntimeError("incorrect guard value " + str(cond))
        guard = cond if guard is None else guard&cond
        _ignore_errors = _ignore_errors or cond.value==0
        LinComb.ONE = guard        
    elif is_base_value(cond):
        if cond==0: raise RuntimeError("unreachable code")
        if cond!=1: raise RuntimeError("incorrect guard value " + str(cond))
    else:
        raise TypeError("unexpected argument type for add_guard: " + str(cond))

    return (_orig_guard,_orig_ignore_errors,_orig_ONE)

def restore_guard(bak):
    global guard, _ignore_errors
    
    (_orig_guard,_orig_ignore_errors,_orig_ONE)=bak
    guard = _orig_guard
    _ignore_errors = _orig_ignore_errors
    LinComb.ONE = _orig_ONE    


def guarded(cond):
    def _guarded(fn):
        def __guarded(*args, **kwargs):
            bak = add_guard(cond)
            
            try:
                ret = fn(*args, **kwargs)
                restore_guard(bak)
            except:
                restore_guard(bak)
                raise
        
            return ret
        
        return __guarded
    return _guarded

def is_guard():
    return (guard is None or guard.value==1)

def if_guard(fn):
    def _if_guard(*args, **kwargs):
        if is_guard():
            return fn(*args, **kwargs)
    return _if_guard

igprint = if_guard(print)

def add_constraint(v,w,y,check=True):
    """
    Add the constraint v * w = y to the constraint system
    Updates running computation hash
    """
    if not guard is None:
        dummy = PrivVal(v.value*w.value-y.value)
        add_constraint_unsafe(v,w,y+dummy)
        add_constraint_unsafe(guard,dummy,LinComb.ZERO)
    else:
        if v.value*w.value!=y.value:
            # note that we do the check over the integers
            if check and not ignore_errors(): raise AssertionError("constraint did not hold")
            
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
    def __lt__(self, other):
        return (other-self-1).check_positive()
    
    def assert_lt(self, other, err=None):
        other = LinComb._ensurelc(other)

        if not ignore_errors():
            if self.value >= other.value:
                raise AssertionError(err if err is not None else str(self.value) + " is not less than " + str(other.value))

        (other-self-1).assert_positive(err=err)
        
    # self<=other, so other-self>=0
    def __le__(self, other):
        return (other-self).check_positive()

    def assert_le(self, other, err=None):
        other = LinComb._ensurelc(other)

        if not ignore_errors():
            if self.value > other.value:
                raise AssertionError(err if err is not None else str(self.value) + " is not less than or equal to " + str(other.value))

        (other-self).assert_positive(err=err)
    
    def __eq__(self, other):
        return (self-other).check_zero()

    def assert_eq(self, other, err=None):
        other = LinComb._ensurelc(other)

        if not ignore_errors():
            if self.value != other.value:
                raise AssertionError(err if err is not None else str(self.value) + " is not equal to " + str(other.value))

        (self-other).assert_zero(err=err)
        
    def __ne__(self, other):
        return (self-other).check_nonzero()

    def assert_ne(self, other, err=None):
        other = LinComb._ensurelc(other)

        if not ignore_errors():
            if self.value == other.value:
                raise AssertionError(err if err is not None else str(self.value) + " is equal to " + str(other.value))

        (self-other).assert_nonzero(err=err)
        
    # self>other, so self-other>0, so self-other-1>=0
    def __gt__(self, other):
        return (self-other-1).check_positive()

    def assert_gt(self, other, err=None):
        other = LinComb._ensurelc(other)

        if not ignore_errors():
            if self.value <= other.value:
                raise AssertionError(err if err is not None else str(self.value) + " is not greater than " + str(other.value))

        (self-other-1).assert_positive(err=err)

    # self>=other, so self-other>=0
    def __ge__(self, other):
        return (self-other).check_positive()

    def assert_ge(self, other, err=None):
        other = LinComb._ensurelc(other)

        if not ignore_errors():
            if self.value < other.value:
                raise AssertionError(err if err is not None else str(self.value) + " is not greater than or equal to " + str(other.value))

        (self-other).assert_positive(err=err)
        
    def __bool__(self):
        raise NotImplementedError("Cannot call __bool__ on a LinComb. \
            Instead of if statements, use if_then_else from pysnark.branching")

    def __add__(self, other):
        """
        Adds a LinComb with an integer or another LinComb
        Costs 0 constraints
        """
        if isinstance(other, int):
            return self + ConstVal(other)
        if isinstance(other, LinComb):
            return LinComb(self.value + other.value, self.lc + other.lc)
        return NotImplemented
    
    def __sub__(self, other):
        """
        Subtracts an integer or another LinComb from a LinComb
        Costs 0 constraints
        """
        return self + (-other)

    def __mul__(self, other):
        """
        Multiplies a LinComb with an integer or another LinComb
        Costs 0 constraints to multiply with an integer
        Costs 1 constraint to multiply with a LinComb
        """
        if isinstance(other, int):
            return LinComb(self.value * other, self.lc * other)
        if isinstance(other, LinComb):
            retval = PrivVal(self.value * other.value)
            add_constraint_unsafe(self, other, retval)
            return retval
        return NotImplemented

    def __truediv__(self, other): 
        """
        Divides a LinComb with an integer or another LinComb using integer division
        Throws ValueError if values are not evenly divisible
        Costs 0 constraints to divide with an integer
        Costs 1 constraint to divide with a LinComb
        """
        if isinstance(other, int):
            if other == 0:
                raise ValueError("Division by zero")
            if is_guard() and (self.value % other == 0):
                return LinComb(self.value // other, self.lc * backend.fieldinverse(other))
            if ignore_errors():
                return LinComb(0, self.lc * backend.fieldinverse(other))
            raise ValueError(str(self.value) + " is not properly divisible by " + str(other))

        if isinstance(other, LinComb):
            if other.value == 0:
                raise ValueError("Division by zero")
            elif is_guard() and (self.value % other.value == 0):
                res = PrivVal(self.value // other.value)
            elif ignore_errors():
                res = PrivVal(0)
            else:
                raise ValueError(str(self.value) + " is not properly divisible by " + str(other.value))
            add_constraint(other, res, self)
            return res

        return NotImplemented
         
    def __floordiv__(self, other):
        """
        Divides a LinComb with an integer or another LinComb using floor division
        Costs 2 * bitlength + 4 constraints for floor division
        """
        res = self.__divmod__(other)
        if res is NotImplemented:
            return NotImplemented
        return res[0]

    def __mod__(self, other):
        """
        Returns the remainder of a LinComb divided with an integer or another LinComb
        Costs 2 * bitlength + 4 constraints for modular division
        """
        res = self.__divmod__(other)
        if res is NotImplemented:
            return NotImplemented
        return res[1]
        
    def __divmod__(self, divisor):
        """
        Divides a LinComb with an integer or another LinComb and returns the quotient and the remainder
        Costs 2 * bitlength + 4 constraints to divide
        """
        if isinstance(divisor, int):
            divisor = ConstVal(divisor)

        if isinstance(divisor, LinComb):
            if divisor.value == 0:
                raise ValueError("Division by zero")
            quo = PrivVal(self.value // divisor.value)
            res = quo * divisor
            rem = PrivVal(self.value - res.value)

            # TODO: Prevent field overflow by a malicious prover
            # Add a constraint ensuring quo * divisor + rem < backend.get_modulus()
            # The check above works over the integers, but not in a finite field

            add_constraint(quo, divisor, self - rem)
            rem.assert_lt(divisor)
            quo.assert_positive()
            return (quo,rem)

        return NotImplemented
    
    def __pow__(self, other, mod=None):
        """
        Raises a LinComb to the power of an integer or a LinComb
        Costs n constraints to raise to an integer power n
        Costs 41 constraints to raise to the power of a LinComb,
        The exponent n must be <= 31 to prevent Python crashing
        """
        if mod != None:
            raise ValueError("Cannot provide modulus")
        if isinstance(other, int):
            if other < 0:
                raise ValueError("Exponent cannot be negative")
            if other == 0:
                return LinComb.ONE
            if other == 1:
                return self
            return self * self ** (other - 1)

        if isinstance(other, LinComb):
            # Obliviously apply repeated squaring
            from .branching import if_then_else

            # Limit exponent to prevent Python crashing with bus error
            if other.value.bit_length() > 5:
                raise ValueError("Power too large")
            other_bits = other.to_bits(bits=5)

            # Compute all powers of value to hide true exponent
            powers = [self]
            curr = self
            for i in range(len(other_bits)):
                curr = curr ** 2
                powers.append(curr)

            # Obliviously pick only the powers we need
            multiplicands = [if_then_else(bit == 1, power, LinComb.ONE) for (bit, power) in zip(other_bits, powers)]
            
            # Multiply the powers together
            res = LinComb.ONE
            for multiplicand in multiplicands:
                res *= multiplicand
            return res

        return NotImplemented
    
    def __lshift__(self, other):
        """
        Shifts a LinComb bitwise to the left
        Costs 0 constraints to shift by an integer number of bits
        Costs 42 constraints to shift by a LinComb number of bits,
        given 41 operations to raise a LinComb to the power of a LinComb
        """
        if isinstance(other, int):
            res = self * (1 << other)
            if res is NotImplemented:
                return NotImplemented
            return res
        if isinstance(other, LinComb):
            res = self * (2 ** other)
            if res is NotImplemented:
                return NotImplemented
            return res
        return NotImplemented
    
    def __rshift__(self, other):
        """
        Shifts a LinComb bitwise to the right
        Costs bitlength + 1 constraints to shift by an integer number of bits
        Costs 2 * bitlength + 45 constraints shift by a LinComb number of bits
        """
        if isinstance(other, int):
            bits = self.to_bits()
            wanted_bits = bits[other:]
            return LinComb.from_bits(wanted_bits)
        if isinstance(other, LinComb):
            res = self // (2 ** other)
            if res is NotImplemented:
                return NotImplemented
            return res
        return NotImplemented
    
    def __and__(self, other):
        """
        Computes the bitwise and of a LinComb with an integer or a LinComb
        Costs 0 operations to and with an integer
        Costs 3 * bitlength + 3 operations to and with a LinComb 
        """
        if isinstance(other, int):
            return PrivVal(self.value & other)
        if isinstance(other, LinComb):
            self_bits = self.to_bits()
            other_bits = other.to_bits()
            res = [x * y for (x,y) in zip(self_bits, other_bits)]
            return LinComb.from_bits(res)
        return NotImplemented

    def __xor__(self, other):
        """
        Computes the bitwise xor of a LinComb with an integer or a LinComb
        Costs 0 operations to xor with an integer
        Costs 3 * bitlength + 3 operations to xor with a LinComb
        """
        if isinstance(other, int):
            return PrivVal(self.value ^ other)
        if isinstance(other, LinComb):
            self_bits = self.to_bits()
            other_bits = other.to_bits()
            res = [x + y - 2 * x * y for (x,y) in zip(self_bits, other_bits)]
            return LinComb.from_bits(res)
        return NotImplemented

    def __or__(self, other):
        """
        Computes the bitwise or of a LinComb with an integer or a LinComb
        Costs 0 operations to or with an integer
        Costs 3 * bitlength + 3 operations to or with a LinComb
        """
        if isinstance(other, int):
            return PrivVal(self.value | other)
        if isinstance(other, LinComb):
            self_bits = self.to_bits()
            other_bits = other.to_bits()
            res = [x + y - x * y for (x,y) in zip(self_bits, other_bits)]
            return LinComb.from_bits(res)
        return NotImplemented

    __radd__ = __add__
    __rmul__ = __mul__

    def __rsub__(self, other):
        return other + (-self)

    def __rtruediv__(self, other):
        return ConstVal(other).__truediv__(self)

    def __rfloordiv__(self, other):
        return ConstVal(other).__floordiv__(self)

    def __rmod__(self, other):
        return ConstVal(other).__mod__(self)

    def __rdivmod__(self, other):
        return ConstVal(other).__divmod__(self)

    def __rpow__(self, other):
        return ConstVal(other).__pow__(self)

    def __rlshift__(self, other):
        return ConstVal(other).__lshift__(self)

    def __rrshift__(self, other):
        return ConstVal(other).__rshift__(self)

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
        inverted_bits = [~x for x in self.to_bits()]
        return LinComb.from_bits(inverted_bits)
        
    def __complex__(self): return NotImplemented
    def __int__(self): raise NotImplementedError("Should not run int() on LinComb")
    def __float__(self): return NotImplemented
    
    def __matmul__(self, other): return NotImplemented
    def __rmatmul__(self, other): return NotImplemented

    def __round__(self, ndigits=None): return NotImplemented
    def __trunc__(self): return NotImplemented
    def __floor__(self): return NotImplemented
    def __ceil__(self): return NotImplemented

    def to_bits(self, bits=None):
        """
        Splits an integer LinComb into an bitlength-length array of LinCombBool bits
        Raises AssertionError if LinComb cannot be represented with bitlength bits
        Costs bitlength + 1 constraints to split a LinComb into bits
        """
        from pysnark.boolean import PrivValBool
        
        if bits is None:
            bits = bitlength

        if not ignore_errors():
            if self.value < 0 or self.value.bit_length() > bits:
                raise AssertionError(str(self.value) + " is not a " + str(bits) + "-bit positive integer")

        # Construct bits
        bits = [PrivValBool((self.value & (1 << ix)) >> ix) for ix in range(bits)]
        
        # Check that bits are equal to self
        (self - LinComb.from_bits(bits)).assert_zero()
        
        return bits
        
    @classmethod
    def from_bits(cls, bits):
        """
        Constructs an integer LinComb out of an array of LinCombBool bits
        Costs 0 constraints to construct a LinComb from bits
        """
        return sum([biti * (1 << i) for (i,biti) in enumerate(bits)])

    """
    Given a value in [-1<<bitlength,1>>bitlength], check if it is positive.
    Note that this works on (bitlength+1)-length values so it works for
    __lt__, etc on bitlength-length values
    """
    def check_positive(self, bits=None):
        """
        Checks if a LinComb is a positive bitlength-bit integer
        Costs bitlength + 2 constraints
        """
        from pysnark.boolean import PrivValBool

        if bits is None:
            bits = bitlength

        if is_guard() and self.value.bit_length() <= bits:
            ret = PrivValBool(1 if self.value >= 0 else 0)
            abs = self.value if self.value >= 0 else -self.value

            bits = [PrivValBool((abs & (1 << ix)) >> ix) for ix in range(bits)]
        elif ignore_errors():
            ret = PrivValBool(0)
            bits = [PrivValBool(0) for _ in range(bits)]
        else:
            raise ValueError(str(self.value) + " is not a " + str(bits) + "-bit integer")
        
        # If ret == 1, then requires that 2 * self = self + sum, so sum = self
        # If ret == 0, this requires that 0 = self + sum, so sum = -self
        add_constraint(2 * ret, self, self + LinComb.from_bits(bits))
        
        return ret
            
    def assert_positive(self, bits=None, err=None):
        """
        Ensures a LinComb is a positive bitlength-bit integer
        Costs bitlength + 1 constraints
        """

        if bits is None:
            bits = bitlength

        if not ignore_errors():
            if self.value < 0 or self.value.bit_length() > bits:
                raise AssertionError(err if err is not None else str(self.value) + " is not a " + str(bits) + "-bit positive integer")

        self.to_bits()
        
    def check_zero(self):
        """
        Checks whether a LinComb is zero
        Costs 3 constraints
        """
        from pysnark.boolean import LinCombBool

        ret = PrivVal(1 if self.value == 0 else 0)
        wit = PrivVal(backend.fieldinverse(self.value + (self.value == 0))) # Add self.value == 0 to prevent ZeroDivisionError
        
        # Trick from Pinocchio paper: if self is zero then ret=1 by first eq,
        # if self is nonzero then ret=0 by second eq
        add_constraint_unsafe(self, wit, LinComb.ONE_SAFE - ret)
        add_constraint_unsafe(self, ret, LinComb.ZERO)

        return LinCombBool(ret)

    def check_nonzero(self):
        """
        Checks whether a LinComb is nonzero
        Costs 3 constraints
        """
        from pysnark.boolean import LinCombBool

        ret = PrivVal(1 if self.value != 0 else 0)
        wit = PrivVal(backend.fieldinverse(self.value + (self.value == 0)))  # Add self.value == 0 to prevent ZeroDivisionError

        # Use nonzero check gadget from Bulletproofs
        add_constraint_unsafe(self, 1 - ret, LinComb.ZERO)
        add_constraint_unsafe(self, wit, ret)

        return LinCombBool(ret)
    
    def assert_zero(self, err=None):
        """
        Ensures a LinComb is zero
        Costs 1 constraint
        """
        if (not ignore_errors()) and self.value!=0:
            raise AssertionError(err if err is not None else str(self.value) + " is not zero")
            
        add_constraint(LinComb.ZERO, LinComb.ZERO, self)
            
    def assert_nonzero(self, err=None):
        """
        Ensures a LinComb is nonzero
        Costs 1 constraint
        """
        if (is_guard()) and self.value!=0:
            wit = PrivVal(backend.fieldinverse(self.value))    
        elif ignore_errors():
            wit = PrivVal(0)
        else:
            raise AssertionError(err if err is not None else str(self.value) + " is zero")
        
        add_constraint(self, wit, LinComb.ONE, check=False)

    def assert_range(self, rangemin, rangemax, err=None):
        """
        Ensures a LinComb is within the range [rangemin, rangemax]
        Costs 2 * bitlength + 3 constraints
        """
        rangemin = LinComb._ensurelc(rangemin)
        rangemax = LinComb._ensurelc(rangemax)

        if not ignore_errors():
            if self.value < rangemin.value or self.value >= rangemax.value:
                raise AssertionError(err if err is not None else str(self.value) + " is not in the range [" + str(rangemin.value) + "," + str(rangemax.value) + ")")

        # Use bounds check gadget from Bulletproofs
        a = self - rangemin
        b = rangemax - self

        (a + b).assert_eq(rangemax - rangemin, err)
        a.assert_positive()
        b.assert_positive()

    @classmethod
    def _ensurelc(cls, val):
        if isinstance(val, LinComb):
            return val
        if isinstance(val, int):
            return LinComb.ONE * val
        raise RuntimeError("Wrong type for LinComb")

LinComb.ZERO = LinComb(0, backend.zero())
LinComb.ONE = LinComb(1, backend.one())
LinComb.ONE_SAFE = LinComb.ONE

def PubVal(val):
    """
    Create an instance variable
    """
    if not isinstance(val, int):
        raise RuntimeError("Wrong type for PubVal")
    return LinComb(val, backend.pubval(val))

def PrivVal(val):
    """
    Create a witness variable
    """
    if not isinstance(val, int):
        raise RuntimeError("Wrong type for PrivVal")
    return LinComb(val, backend.privval(val))

def ConstVal(val):
    """
    Creates a LinComb representing a constant without creating a witness or instance variable
    Should be used carefully. Using LinCombs instead of integers where not needed will hurt performance
    """
    if not isinstance(val, int):
        raise RuntimeError("Wrong type for ConstVal")
    return LinComb(val, backend.one() * val)

def for_each_in(converter, struct):
    """ Recursively traversing all lists and tuples in struct, apply f to each
        element that is an instance of cls. Returns structure with f applied. """
    if isinstance(struct, list):
        return list(map(lambda x: for_each_in(converter, x), struct))
    elif isinstance(struct, tuple):
        return tuple(map(lambda x: for_each_in(converter, x), struct))
    elif isinstance(struct, dict):
        return {k: for_each_in(converter, struct[k]) for k in struct}
    else:
        return converter(struct)

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
        from pysnark.fixedpoint import PubValFxp, LinCombFxp
        from pysnark.boolean import PubValBool, LinCombBool

        if kwargs: raise ValueError("@snark-decorated functions cannot have keyword arguments")

        argscopy = for_each_in(lambda x: PubVal(x) if isinstance(x,int) else x, args)
        argscopy = for_each_in(lambda x: PubValFxp(x) if isinstance(x,float) else x, argscopy)
        argscopy = for_each_in(lambda x: PubValBool(x) if isinstance(x,bool) else x, argscopy)
        ret = fn(*argscopy, **kwargs)
        retcopy = for_each_in(lambda x: x.val() if isinstance(x,LinComb) else x, ret)
        retcopy = for_each_in(lambda x: x.val() if isinstance(x,LinCombFxp) else x, retcopy)
        retcopy = for_each_in(lambda x: x.val() if isinstance(x,LinCombBool) else x, retcopy)

        return retcopy
        
    return snark__

autoprove = True

def final():
    if autoprove: backend.prove()

import atexit
from .atexitmaybe import maybe
# lambda used here to make sure that backend variable is read at the end
atexit.register(maybe(final))
