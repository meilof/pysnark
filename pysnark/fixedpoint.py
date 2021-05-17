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

import pysnark.runtime
from pysnark.runtime import LinComb, is_base_value, PrivVal, PubVal

"""
Support for fixed-point computations
"""

class LinCombFxp:
    """
    Variable representing a fixed-point number. Number x is represented as integer
    :math:`x * 2^r`, where r is the resolution :py:data:`VarFxp.res`
    """
    
    res = 8

    def __init__(self, lc):
        if not isinstance(lc, LinComb): raise RuntimeError("wrong type for LinCombFxp")
        self.lc = lc

    @classmethod
    def fromvar(cls, var, doconvert):
        if not isinstance(var, LinComb): raise RuntimeError("wrong type for fromvar")
        if doconvert:
            return cls(var*(1<<LinCombFxp.res))
        else:
            return cls(var)
    
    @classmethod
    def tofloat(self, val):
        return float(val)/(1<<LinCombFxp.res)
    
    def val(self):
        return LinCombFxp.tofloat(self.lc.val())

    def __repr__(self):
        return "{"+str(LinCombFxp.tofloat(self.lc.value))+"}"
    
    @classmethod
    def _ensurefxp(cls, val):
        if isinstance(val,LinCombFxp):
            return val
        elif isinstance(val,LinComb):
            return cls.fromvar(val, True)
        else:
            v = _tofxpval(val, True)
            return cls(LinComb.ONE*v)
    
    def __add__(self, other):
        other = self._ensurefxp(other)
        return LinCombFxp(self.lc+other.lc)
        
    __radd__ = __add__
    
    def __sub__(self, other):
        return self+(-other)

    def __mul__(self, other):
        if is_base_value(other):
            return LinCombFxp(self.lc*other)
        
        other = self._ensurefxp(other)
        if other is NotImplemented: return NotImplemented
        
        ret = LinCombFxp(PrivVal((self.lc.value*other.lc.value+(1<<(LinCombFxp.res-1)))>>LinCombFxp.res))
            
        # mul error: should be in [-2^f,2^f]
        diff = (1<<LinCombFxp.res)*ret.lc-self.lc*other.lc
        (diff + (1<<LinCombFxp.res)).assert_positive(LinCombFxp.res+1)
        ((1<<LinCombFxp.res) - diff).assert_positive(LinCombFxp.res+1)

        return ret        
    
    __rmul__ = __mul__
    
    def __truediv__(self, other): 
        other = self._ensurefxp(other)
        if other is NotImplemented: return NotImplemented

        ret = LinCombFxp(PrivVal(int(float(self.lc.value)*(1<<LinCombFxp.res)/float(other.lc.value)+0.5)))

        # division error: should be in [-other,other]
        df=self.lc*(1<<LinCombFxp.res)-ret.lc*other.lc
        (other.lc-df).assert_positive()
        (other.lc+df).assert_positive()
        
        return ret
         
    def __floordiv__(self, other):
        return NotImplemented

    def __mod__(self, other):
        return NotImplemented
        
    def __divmod__(self, divisor):
        return NotImplemented

    def __rtruediv__(self, other):
        return NotImplemented

    def __neg__(self):
        return LinCombFxp(-self.lc)
    
    def __lt__(self, other): return self.lc < self._ensurefxp(other).lc
    def __le__(self, other): return self.lc <= self._ensurefxp(other).lc
    def __eq__(self, other): return self.lc == self._ensurefxp(other).lc
    def __ne__(self, other): return self.lc != self._ensurefxp(other).lc
    def __gt__(self, other): return self.lc > self._ensurefxp(other).lc
    def __ge__(self, other): return self.lc >= self._ensurefxp(other).lc
        
def _tofxpval(val, doconvert):
    if isinstance(val, float):
        return int(val*(1<<LinCombFxp.res)+0.5)
    elif doconvert:
        return val*(1<<LinCombFxp.res)
    else:
        return val
        
def PubValFxp(val, doconvert=True):
    val = _tofxpval(val, doconvert)
    return LinCombFxp(PubVal(val))

def PrivValFxp(val, doconvert=True):
    val = _tofxpval(val, doconvert)
    return LinCombFxp(PrivVal(val))

