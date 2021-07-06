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
from pysnark.boolean import LinCombBool

"""
Support for fixed-point computations
Costs 0 constraints to convert a LinComb to a LinCombFxp
A float x is represented as the integer x * (1 << res)
"""

# Fixed point resolution
resolution = 8

class LinCombFxp:
    def __init__(self, lc, scale=True):
        if not isinstance(lc, LinComb):
            raise RuntimeError("Wrong type for LinCombFxp")
        
        # Add scaling if needed
        if scale:
            lc = LinCombFxp.add_scaling(lc)

        self.lc = lc
    
    @classmethod
    def add_scaling(cls, val):
        """
        Converts an integer, float, or LinComb into the internal fixed point representation
        Does not convert the input into a LinCombFxp
        """
        if isinstance(val, LinComb) or isinstance(val, LinCombBool):
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
        return "{" + str(self.lc.value) + "}"
    
    @classmethod
    def _ensurefxp(cls, val):
        """
        Converts an integer, float, or LinComb into the internal fixed point representation
        and converts the input into a LinCombFxp
        """
        if isinstance(val, LinCombFxp):
            return val
        if isinstance(val, LinComb):
            return LinCombFxp(val)
        if isinstance(val, LinCombBool):
            return LinCombFxp(val.lc)
        if isinstance(val, int) or isinstance(val, float):
            val = LinCombFxp.add_scaling(val)
            return LinCombFxp(ConstVal(val), False)
        raise RuntimeError("Wrong type for LinCombFxp")
    
    def __add__(self, other):
        """
        Adds a LinCombFxp with an integer, float, LinComb, or another LinCombFxp
        Costs 0 constraints
        """
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, LinComb):
            other = LinCombFxp.add_scaling(other)
            return LinCombFxp(self.lc + other, False)
        if isinstance(other, LinCombFxp):
            return LinCombFxp(self.lc + other.lc, False)
        return NotImplemented

    __radd__ = __add__
    
    def __sub__(self, other):
        """
        Subtracts a LinCombFxp by an integer, float, LinComb, or another LinCombFxp
        Costs 0 constraints
        """
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
            return LinCombFxp(self.lc * other, False)
        if isinstance(other, float):
            other = LinCombFxp.add_scaling(other)
            return LinCombFxp((self.lc * other) / (1 << resolution), False)
        if isinstance(other, LinComb):
            return LinCombFxp(self.lc * other, False)
        if isinstance(other, LinCombFxp):
            return LinCombFxp((self.lc * other.lc) / (1 << resolution), False)
        return NotImplemented

    __rmul__ = __mul__
    
    def __truediv__(self, other):
        """
        Divides a LinCombFxp with an integer, float, LinComb, or another LinCombFxp
        Costs 2 * bitlength + 4 constraints to divide
        """
        if isinstance(other, int):
            return LinCombFxp(self.lc // other, False)
        if isinstance(other, float):
            other = LinCombFxp.add_scaling(other)
            return LinCombFxp(self.lc * (1 << resolution) // other, False)
        if isinstance(other, LinComb):
            other = LinCombFxp.add_scaling(other)
            return LinCombFxp(self.lc * (1 << resolution) // other, False)
        if isinstance(other, LinCombFxp):
            return LinCombFxp(self.lc * (1 << resolution) // other.lc, False)
        return NotImplemented
         
    def __floordiv__(self, other):
        """
        Divides LinCombFxp by an integer, float, LinComb, or LinCombFxp using floor division
        Costs 2 * bitlength + 4 constraints for floor division
        """
        res = self.__divmod__(other)
        if res is NotImplemented:
            return NotImplemented
        return res[0]

    def __mod__(self, other):
        """
        Returns the remainder of a LinCombFxp divided with an integer, float, LinComb, or LinCombFxp 
        Costs 2 * bitlength + 4 constraints for modular division
        """
        res = self.__divmod__(other)
        if res is NotImplemented:
            return NotImplemented
        return res[1]
        
    def __divmod__(self, divisor):
        """
        Divides a LinCombFxp with an integer, float, LinComb, or LinCombFxp and returns the quotient and the remainder
        Costs 2 * bitlength + 4 constraints to divide
        """
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
        quo = LinCombFxp(quo)
        rem = LinCombFxp(rem, False)
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
        return LinCombFxp(-self.lc, False)
    
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
        """
        Raises a LinCombFxp to the power of an integer
        Costs n-1 constraints to raise to the power n
        The exponent n must be <= 31 to prevent Python crashing
        """
        if mod!=None: raise ValueError("cannot provide modulus")
        if not isinstance(other, int): return NotImplemented
        if other<0: raise ValueError("exponent cannot be negative", other)
        if other==0: return LinCombFxp(LinComb.ONE)
        if other==1: return self
        return self * self ** (other - 1)
    
    def __lshift__(self, other): return LinCombFxp(self.lc<<other, False)

    def __rshift__(self, other): return LinCombFxp(self.lc>>other, False)
        
    def __pos__(self):
        return self
    
    def __abs__(self):
        from .branching import if_then_else
        return if_then_else(self >= 0, self, -self)

    def __int__(self): raise NotImplementedError("Should not run int() on LinComb")
        
    def check_positive(self): return self.lc.check_positive()
    def assert_positive(self): self.lc.assert_positive()
    def check_zero(self): return self.lc.check_zero()
    def check_nonzero(self): return self.lc.check_nonzero()
    def assert_zero(self): self.lc.assert_zero()
    def assert_nonzero(self): self.lc.assert_nonzero()
    def assert_range(self, minrange, maxrange):
        minrange = LinCombFxp._ensurefxp(minrange)
        maxrange = LinCombFxp._ensurefxp(maxrange)
        self.lc.assert_range(minrange.lc, maxrange.lc)

def PubValFxp(val, doconvert=True):
    if not isinstance(val, int) and not isinstance(val, float):
        raise RuntimeError("Wrong type for PubValFxp")
    if doconvert:
        val = LinCombFxp.add_scaling(val)
    return LinCombFxp(PubVal(val), False)

def PrivValFxp(val, doconvert=True):
    if not isinstance(val, int) and not isinstance(val, float):
        raise RuntimeError("Wrong type for PrivValFxp")
    if doconvert:
        val = LinCombFxp.add_scaling(val)
    return LinCombFxp(PrivVal(val), False)