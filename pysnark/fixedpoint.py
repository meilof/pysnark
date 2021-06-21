# Portions copyright (C) Meilof Veeningen, 2019

# Portions copyright (c) 2016-2018 Koninklijke Philips N.V. All rights
# reserved. A copyright license for redistribution and use in source and
# binary forms, with or without modification, is hereby granted for
# non-commercial, experimental and research purposes, provided that the
# following conditions are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimers.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimers in the
#   documentation and/or other materials provided with the distribution. If
#   you wish to use this software commercially, kindly contact
#   info.licensing@philips.com to obtain a commercial license.
#
# This license extends only to copyright and does not include or grant any
# patent license or other license whatsoever.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import warnings
import pysnark.runtime
from pysnark.runtime import LinComb, PrivVal, PubVal, ConstVal

"""
Support for fixed-point computations
Costs 0 constraints to convert a LinComb to a LinCombFxp
A float x is represented as the integer x * (1 << res)
"""

# Fixed point resolution
resolution = 8

class LinCombFxp:
    def __init__(self, lc):
        if not isinstance(lc, LinComb):
            raise RuntimeError("Wrong type for LinCombFxp")
        self.lc = lc
    
    @classmethod
    def add_scaling(cls, val):
        """
        Converts an integer, float, or LinComb into the internal fixed point representation
        Does not convert the input into a LinCombFxp
        """
        if isinstance(val, LinComb):
            return val * (1 << resolution)
        if isinstance(val, int):
            return val * (1 << resolution)
        if isinstance(val, float):
            res = val * (1 << resolution)
            if res - int(res) != 0:
                warnings.warn("Potential data loss due to low fixed point resolution")
            return int(res)
        raise RuntimeError("Wrong type for add_scaling")

    @classmethod
    def remove_scaling(self, val):
        """
        Converts an internal fixed point representation into a float value
        """
        if isinstance(val, LinComb):
            return float(val.val()) / (1 << resolution)
        if isinstance(val, int) or isinstance(val, float):
            return float(val) / (1 << resolution)
        raise RuntimeError("Wrong type for add_scaling")
    
    def val(self):
        return LinCombFxp.remove_scaling(self.lc.val())

    def __repr__(self):
        return "{" + str(self.val()) + "}"
    
    @classmethod
    def _ensurefxp(cls, val):
        """
        Converts an integer, float, or LinComb into the internal fixed point representation
        and converts the input into a LinCombFxp
        """
        if isinstance(val, LinCombFxp):
            return val
        if isinstance(val, LinComb):
            val = LinCombFxp.add_scaling(val)
            return LinCombFxp(val)
        if isinstance(val, int) or isinstance(val, float):
            val = LinCombFxp.add_scaling(val)
            return LinCombFxp(ConstVal(val))
        raise RuntimeError("Wrong type for _ensurefxp")
    
    def __add__(self, other):
        """
        Adds a LinCombFxp with an integer, float, LinComb, or another LinCombFxp
        Costs 0 constraints
        """
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, LinComb):
            other = LinCombFxp.add_scaling(other)
            return LinCombFxp(self.lc + other)
        if isinstance(other, LinCombFxp):
            return LinCombFxp(self.lc + other.lc)
        return NotImplemented

    __radd__ = __add__
    
    def __sub__(self, other):
        return self + (-other)
    
    def __rsub__(self, other):
        return other + (-self)

    def __mul__(self, other):
        """
        Multiplies a LinCombFxp with an integer, float, LinComb, or another LinCombFxp
        Costs 0 constraints to multiply with an integer or a float
        Costs 1 constraint to multiply with a LinComb or LinCombFxp
        """
        if isinstance(other, int):
            return LinCombFxp(self.lc * other)
        if isinstance(other, float):
            other = LinCombFxp.add_scaling(other)
            return LinCombFxp((self.lc * other) / (1 << resolution))
        if isinstance(other, LinComb):
            other = LinCombFxp.add_scaling(other)
            return LinCombFxp((self.lc * other) / (1 << resolution))
        if isinstance(other, LinCombFxp):
            return LinCombFxp((self.lc * other.lc) / (1 << resolution))
        return NotImplemented

    __rmul__ = __mul__
    
    def __truediv__(self, other):
        """
        Divides a LinCombFxp with an integer, float, LinComb, or another LinCombFxp
        Costs 0 constraints to divide with an integer or a float
        Costs 1 constraint to divide with a LinComb or LinCombFxp
        """
        if isinstance(other, int):
            return LinCombFxp(self.lc / other)
        if isinstance(other, float):
            other = LinCombFxp.add_scaling(other)
            return LinCombFxp(self.lc * (1 << resolution) / other)
        if isinstance(other, LinComb):
            other = LinCombFxp.add_scaling(other)
            return LinCombFxp(self.lc * (1 << resolution) / other)
        if isinstance(other, LinCombFxp):
            return LinCombFxp(self.lc * (1 << resolution) / other.lc)
        return NotImplemented
         
    def __floordiv__(self, other):
        res = self.__divmod__(other)
        if res is NotImplemented:
            return NotImplemented
        return res[0]

    def __mod__(self, other):
        res = self.__divmod__(other)
        if res is NotImplemented:
            return NotImplemented
        return res[1]
        
    def __divmod__(self, divisor):
        if isinstance(divisor, int) or isinstance(divisor, float) or isinstance(divisor, LinComb):
            divisor = LinCombFxp.add_scaling(divisor)
            res = self.lc.__divmod__(divisor)
        elif isinstance(divisor, LinCombFxp):
            res = self.lc.__divmod__(divisor.lc)
        else:
            return NotImplemented
        if res is NotImplemented:
            return NotImplemented
        quo, rem = res
        quo = LinCombFxp(LinCombFxp.add_scaling(quo))
        rem = LinCombFxp(rem)
        return (quo,rem)

    def __rtruediv__(self, other):
        other = LinCombFxp._ensurefxp(other)
        return other.__truediv__(self)

    def __rfloordiv__(self, other):
        other = LinCombFxp._ensurefxp(other)
        return other.__floordiv__(self)

    def __rmod__(self, other):
        other = LinCombFxp._ensurefxp(other)
        return other.__mod__(self)

    def __neg__(self):
        return LinCombFxp(-self.lc)
    
    def __lt__(self, other): return self.lc < self._ensurefxp(other).lc
    def __le__(self, other): return self.lc <= self._ensurefxp(other).lc
    def __eq__(self, other): return self.lc == self._ensurefxp(other).lc
    def __ne__(self, other): return self.lc != self._ensurefxp(other).lc
    def __gt__(self, other): return self.lc > self._ensurefxp(other).lc
    def __ge__(self, other): return self.lc >= self._ensurefxp(other).lc
    
    def assert_lt(self, other, err=None): self.lc.assert_lt(self._ensurefxp(other).lc)
    def assert_le(self, other, err=None): self.lc.assert_le(self._ensurefxp(other).lc)
    def assert_eq(self, other, err=None): self.lc.assert_eq(self._ensurefxp(other).lc)
    def assert_ne(self, other, err=None): self.lc.assert_ne(self._ensurefxp(other).lc)
    def assert_gt(self, other, err=None): self.lc.assert_gt(self._ensurefxp(other).lc)
    def assert_ge(self, other, err=None): self.lc.assert_ge(self._ensurefxp(other).lc)
        
    def __bool__(self): return bool(self.lc)
        
    def __pow__(self, other, mod=None):
        """ Exponentiation with public integral power p>=0 """
        if mod!=None: raise ValueError("cannot provide modulus")
        if not is_base_value(other): return NotImplemented
        if other<0: raise ValueError("exponent cannot be negative", other)
        if other==0: return LinCombFxp(add_scaling(LinComb.ONE))
        if other==1: return self
        return self*pow(self, other-1)
    
    def __lshift__(self, other): return LinCombFxp(self.lc<<other)

    def __rshift__(self, other): return LinCombFxp(self.lc>>other)
        
    def __pos__(self):
        return self
    
    def __abs__(self):
        from .branching import if_then_else
        return if_then_else(self>=0, self, -self)

    def __int__(self): raise NotImplementedError("Should not run int() on LinComb")
        
    def check_positive(self): return self.lc.check_positive()
    def assert_positive(self): self.lc.assert_positive()
    def check_zero(self): return self.lc.check_zero()
    def assert_zero(self): self.lc.assert_zero()
    def assert_nonzero(self): self.lc.assert_nonzero()
        
    def __if_then_else__(self, other, cond):
        falsev = self._ensurefxp(other).lc
        return LinCombFxp(falsev+(self.lc-falsev)*cond)

def PubValFxp(val, doconvert=True):
    if doconvert:
        val = LinCombFxp.add_scaling(val)
    return LinCombFxp(PubVal(val))

def PrivValFxp(val, doconvert=True):
    if doconvert:
        val = LinCombFxp.add_scaling(val)
    return LinCombFxp(PrivVal(val))