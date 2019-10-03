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
from pysnark.runtime import LinComb, is_base_value

"""
Support for fixed-point computations
"""

class LinCombFxp(LinComb):
    """
    Variable representing a fixed-point number. Number x is represented as integer
    :math:`x * 2^r`, where r is the resolution :py:data:`VarFxp.res`
    """

    res = 8     #: Resulution for fixed-point numbers

    @classmethod
    def fromvar(cls, var, doconvert):
        if doconvert:
            return cls(var.value*(1<<cls.res), var.lc*(1<<cls.res))
        else:
            return cls(var.value, var.lc)
    
    @classmethod
    def tofloat(self, val):
        return float(val)/(1<<LinCombFxp.res)
    
    def val(self):
        return LinCombFxp.tofloat(self.value)

    def __repr__(self):
        return "{"+str(LinCombFxp.tofloat(self.value))+"}"
    
    @classmethod
    def _ensurefxp(cls, val):
        if isinstance(val,LinCombFxp):
            return val
        elif isinstance(val,LinComb):
            return LinCombFxp.fromvar(val, True)
        else:
            v = _tofxpval(val, True)
            return LinCombFxp(v, LinComb.ONE.lc*v)
    
    def __add__(self, other):
        other = self._ensurefxp(other)
        
        if isinstance(other, LinCombFxp):
            return LinCombFxp(self.value+other.value, self.lc+other.lc)
        elif is_base_value(other):
            return self + other*LinComb.ONE
        else:
            return NotImplemented
        
    __radd__ = __add__

    def __mul__(self, other):
        if is_base_value(other):
            return LinCombFxp(self.value*other, self.lc*other)
        
        other = self._ensurefxp(other)
        if other is NotImplemented: return NotImplemented
        
        ret = PrivValFxp((self.value*other.value+(1<<(LinCombFxp.res-1)))>>LinCombFxp.res, False)
            
        # mul error: should be in [-2^f,2^f]
        diff = LinComb.__add__((1<<LinCombFxp.res)*ret, -LinComb.__mul__(self, other))
        (diff + (1<<LinCombFxp.res)).assert_positive(LinCombFxp.res+1)
        ((1<<LinCombFxp.res) - diff).assert_positive(LinCombFxp.res+1)

        return ret        
    
    __rmul__ = __mul__
    
    def __truediv__(self, other): 
        other = self._ensurefxp(other)
        if other is NotImplemented: return NotImplemented

        ret = PrivValFxp(int(float(self.value)*(1<<LinCombFxp.res)/float(other.value)+0.5),False)

        # division error: should be in [-other,other]
        df=LinComb.__mul__(self, 1<<LinCombFxp.res)-LinComb.__mul__(ret,other)    
        LinComb.__add__(other, -df).assert_positive()
        LinComb.__add__(other, df).assert_positive()
        
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
        return LinCombFxp(-self.value, -self.lc)
        
def _tofxpval(val, doconvert):
    if isinstance(val, float):
        return int(val*(1<<LinCombFxp.res)+0.5)
    elif doconvert:
        return val*(1<<LinCombFxp.res)
    else:
        return val
        
def PubValFxp(val, doconvert=True):
    val = _tofxpval(val, doconvert)
    return LinCombFxp(val, pysnark.runtime.backend.pubval(val))

def PrivValFxp(val, doconvert=True):
    val = _tofxpval(val, doconvert)
    return LinCombFxp(val, pysnark.runtime.backend.privval(val))

