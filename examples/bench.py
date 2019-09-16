# Copyright (C) Meilof Veeningen

import pysnark.runtime

from pysnark.runtime import PrivVal, LinComb, benchmark, guarded
from pysnark.branching import if_then_else, _while

def count_ops(fn):
    numc = 0
    def callback(num):
        nonlocal numc
        numc = num
    
    benchmark(callback)(fn)()
    
    return numc

def benchmark_con_bl(fn):
    # unguarded
    pysnark.runtime.bitlength = 3
    op1 = count_ops(fn)
    pysnark.runtime.bitlength = 5
    op2 = count_ops(fn)
    if op1!=op2:
        raise AssertionError("benchmark_const_nl: function not independent from bitlength")
        
    pysnark.runtime.bitlength = 3
    op3 = count_ops(guarded(LinComb.ONE)(fn))
    pysnark.runtime.bitlength = 5
    op4 = count_ops(guarded(LinComb.ONE)(fn))
    if op3!=op4:
        raise AssertionError("benchmark_const_nl: function not independent from bitlength")
        
    return str(op1) + " [" + str(op3) + "]"

def benchmark_lin_bl(fn):
    pysnark.runtime.bitlength = 3
    op1 = count_ops(fn)
    pysnark.runtime.bitlength = 5
    op2 = count_ops(fn)
    pysnark.runtime.bitlength = 7
    op3 = count_ops(fn)
    coef = (op2-op1)//2
    const = op1-3*coef
    if op3!=const+7*coef:
        raise AssertionError("benchmark_lin_bl: constraints not linear in bitlength")
        
    pysnark.runtime.bitlength = 3
    op4 = count_ops(guarded(LinComb.ONE)(fn))
    pysnark.runtime.bitlength = 5
    op5 = count_ops(guarded(LinComb.ONE)(fn))
    pysnark.runtime.bitlength = 7
    op6 = count_ops(guarded(LinComb.ONE)(fn))
    coef2 = (op5-op4)//2
    const2 = op4-3*coef
    if op6!=const2+7*coef2:
        raise AssertionError("benchmark_lin_bl: constraints not linear in bitlength")

    return str(coef)+"*k+"+str(const) + " [" + str(coef2)+"*k+"+str(const2) + "]"

print("__lt__              ", benchmark_lin_bl(lambda:LinComb.ZERO<LinComb.ZERO))
print("assert_lt           ", benchmark_lin_bl(lambda:LinComb.ZERO.assert_lt(1)))

print("__le__              ", benchmark_lin_bl(lambda:LinComb.ZERO<=LinComb.ZERO))
print("assert_le           ", benchmark_lin_bl(lambda:LinComb.ZERO.assert_le(1)))

print("__eq__              ", benchmark_con_bl(lambda:LinComb.ZERO==LinComb.ZERO))
print("assert_eq           ", benchmark_con_bl(lambda:LinComb.ZERO.assert_eq(LinComb.ZERO)))

print("__ne__              ", benchmark_con_bl(lambda:LinComb.ZERO!=LinComb.ZERO))
print("assert_ne           ", benchmark_con_bl(lambda:LinComb.ZERO.assert_ne(LinComb.ONE)))

print("__gt__              ", benchmark_lin_bl(lambda:LinComb.ZERO>LinComb.ZERO))
print("assert_gt           ", benchmark_lin_bl(lambda:LinComb.ONE.assert_gt(0)))

print("__ge__              ", benchmark_lin_bl(lambda:LinComb.ZERO>=LinComb.ZERO))
print("assert_ge           ", benchmark_lin_bl(lambda:LinComb.ZERO.assert_ge(0)))

print("__add__ (base)      ", benchmark_con_bl(lambda:LinComb.ZERO+0))
print("__add__ (lc)        ", benchmark_con_bl(lambda:LinComb.ZERO+LinComb.ZERO))

print("__sub__ (base)      ", benchmark_con_bl(lambda:LinComb.ZERO-0))
print("__sub__ (lc)        ", benchmark_con_bl(lambda:LinComb.ZERO-LinComb.ZERO))

print("__mul__ (const)     ", benchmark_con_bl(lambda:LinComb.ZERO*0))
print("__mul__ (val)       ", benchmark_con_bl(lambda:LinComb.ZERO*LinComb.ZERO))

print("__truediv__ (const) ", benchmark_con_bl(lambda:LinComb.ONE/1))
print("__truediv__ (val)   ", benchmark_con_bl(lambda:LinComb.ONE/LinComb.ONE))

#    def __floordiv__(self, other):
#        """ Division with rounding """
#        return self.__divmod__(other)[0]
#
#    def __mod__(self, other):
#        if other&(other-1)==0:
#            # this is faster for powers of two
#            return LinComb.from_bits(self.to_bits()[:other.bit_length()-1])
#        
#        return self.__divmod__(other)[1]
#        
#    def __divmod__(self, divisor):
#        """ Division by public value """
#        
#        if not is_base_value(divisor): return NotImplemented
#        
#        if divisor==0: raise ValueError("division by zero")
#        
#        quo = PrivVal(self.value//divisor)
#        rem = PrivVal(self.value-quo.value*divisor)
# 
#        rem.assert_positive(divisor.bit_length())
#        if divisor&(divisor-1)!=0: rem.assert_lt(divisor) # not needed for powers of two
#        quo.assert_positive()
#        (self-divisor*quo-rem).assert_zero()
#        
#        return (quo,rem)
#    
#    def __pow__(self, other, mod=None):
#        """ Exponentiation with public integral power p>=0 """
#        if mod!=None: raise ValueError("cannot provide modulus")
#        if not is_base_value(other): return NotImplemented
#        if other<0: raise ValueError("exponent cannot be negative", other)
#        if other==0: return LinComb.ONE
#        if other==1: return self
#        return self*pow(self, other-1)
#    
#    def __lshift__(self, other):
#        """ Left-shift with public value """
#        # TODO: extend to secret offset?
#        if not is_base_ovalue(other): return NotImplemented
#        return self*(1<<other)
#    
#    def __rshift__(self, other):
#        """ Right-shift with public value """
#        # TODO: extend to secret offset?
#        if not is_base_ovalue(other): return NotImplemented
#        return LinComb.from_bits(self.to_bits[other:])
#    
#    def _check_both_bits(self, other):
#        if ignore_errors: return
#        
#        if self.value !=0 and self.value!=1: raise ValueError("not a bit: " + str(self.value))
#            
#        if isinstance(other, LinComb) and (other.value==0 or other.value==1): return
#        if is_base_value(other) and (other==0 or other==1): return
#        raise ValueError("not a bit: " + str(other))
#    
#    def __and__(self, other):
#        """ Bitwise and &. Cost: 1 constraint """
#        self._check_both_bits(other)
#        return self * other
#
#    def __xor__(self, other):
#        """Bitwise exclusive-or ^. Cost: 1 constraint """
#        self._check_both_bits(other)
#        return self + other - 2 * self * other
#
#    def __or__(self, other):
#        """Bitwise or |. Cost: 1 constraint """
#        self._check_both_bits(other)
#        return self + other - self * other
#
#    __radd__ = __add__
#
#    def __rsub__(self, other):
#        return other+(-self)
#    
#    __rmul__ = __mul__
#    
#    def __rmatmul__(self, other): return NotImplemented
#
#    def __rtruediv__(self, other):
#        """ Proper division by LinComb """
#        if not is_base_value(other): return NotImplemented
#        
#        if other % self.value != 0:
#            raise ValueError(str(other.value) + " is not properly divisible by " + str(self.value))
#            
#        res = PrivVal(other/self.value)
#        do_add_constraint(self, res, other*LinComb.ONE)
#        return res
#        
#    def __rfloordiv__(self, other): return NotImplemented
#    def __rmod__(self, other): return NotImplemented
#    def __rdivmod__(self, other): return NotImplemented
#    def __rpow__(self, other): return NotImplemented
#    def __rlshift__(self, other): return NotImplemented
#    def __rrshift__(self, other): return NotImplemented
#
#    __rand__ = __and__
#    __rxor__ = __xor__
#    __ror__ = __or__
#
#    def __neg__(self):
#        return LinComb(-self.value, -self.lc)
#    
#    def __pos__(self):
#        return self
#    
#    def __abs__(self):
#        from .branching import if_then_else
#        return if_then_else(self>=0, self, -self)
#
#    def __invert__(self):
#        # we do not want to do ~1=0 and ~0=1 since this is also not true for native ints
#        raise NotImplementedError("Operator ~ not supported. For binary not, use 1-x")
#        
#    def __complex__(self): return NotImplemented
#    def __int__(self): raise NotImplementedError("Should not run int() on LinComb")
#    def __float__(self): return NotImplemented
#    
#    def __round__(self, ndigits=None): return NotImplemented
#    def __trunc__(self): return NotImplemented
#    def __floor__(self): return NotImplemented
#    def __ceil__(self): return NotImplemented
#
#    def assert_bool(self):
#        add_constraint(self, 1-self, LinComb.ZERO)
#
#    def assert_bool_unsafe(self):
#        add_constraint_unsafe(self, 1-self, LinComb.ZERO)
#        
#    def to_bits(self, bits=bitlength):
#        if (not ignore_errors) and (self.value<0 or self.value.bit_length()>bits):
#            raise ValueError("value " + str(self.value) + " is not a " + str(bits) + "-bit positive integer")
#            
#        bits = [PrivVal((self.value&(1<<ix))>>ix) for ix in range(bits)]
#        for bit in bits: bit.assert_bool_unsafe()
#            
#        (self-LinComb.from_bits(bits)).assert_zero()
#        
#        return bits
#        
#    @classmethod
#    def from_bits(cls, bits):
#        return sum([biti*(1<<i) for (i,biti) in enumerate(bits)])
#        
#    """
#    Given a value in [-1<<bitlength,1>>bitlength], check if it is positive.
#    Note that this works on (bitlength+1)-length values so it works for
#    __lt__, etc on bitlength-length values
#    """
#    def check_positive(self, bits=bitlength):
#        if (not ignore_errors) and self.value.bit_length()>bits:
#            raise ValueError("value " + str(self.value) + " is not a " + str(bits) + "-bit integer")
#            
#        ret = PrivVal(1 if self.value>=0 else 0)
#        abs = self.value if self.value>=0 else -self.value
#        
#        bits = [PrivVal((abs&(1<<ix))>>ix) for ix in range(bits)]
#        for bit in bits: bit.assert_bool_unsafe()
#            
#        # if ret==1, then requires that 2*self=self+sum, so sum=self
#        # if ret==0, this requires that 0=self+sum, so sum=-self
#        add_constraint(2*ret, self, self+LinComb.from_bits(bits))
#        
#        return ret
#            
#    def assert_positive(self, bits=bitlength):
#        self.to_bits(bits)
#        
#    def check_zero(self):
#        ret = PrivVal(1 if self.value==0 else 0)
#        
#        wit = PrivVal(backend.fieldinverse(self.value+ret.value))  # add ret.value so always nonzero
#        
#        # Trick from Pinocchio paper: if self is zero then ret=1 by first eq,
#        # if self is nonzero then ret=0 by second eq
#        add_constraint_unsafe(self, wit, 1-ret)
#        add_constraint_unsafe(self, ret, LinComb.ZERO)
#        
#        return ret
#    
#    def assert_zero(self):
#        if (not ignore_errors) and self.value!=0:
#            raise ValueError("Value " + str(self.value) + " is not zero")
#            
#        add_constraint(LinComb.ZERO, LinComb.ZERO, self)        
#            
#    def assert_nonzero(self):
#        if (not ignore_errors) and self.value==0:
#            raise ValueError("Value " + str(self.value) + " is not zero")
#            
#        wit = PrivVal(backend.fieldinverse(self.value if self.value!=0 else 1))
#        add_constraint(self, wit, LinComb.ONE)