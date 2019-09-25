# Portions copyright (c) 2019 Meilof Veeningen. See LICENSE.md.
#
# Portions copyright (c) 2016-2018 Koninklijke Philips N.V. All rights
# copyright license for redistribution and use in source and binary forms,
# with or without modification, is hereby granted for non-commercial,
# experimental and research purposes, provided that the following conditions
# are met:
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

from .runtime import PrivVal, LinComb, is_base_value, ignore_errors

from .branching import if_then_else
from .linalg import lin_comb

class Array:
    def __init__(self, vals):
        if isinstance(vals, ArrayRow):
            self.arr = list(vals.arr)
        else:
            self.arr = list(vals)

    def __repr__(self):
        return self.arr.__repr__()

    def __getitem__(self, item):
        if isinstance(item, tuple) and len(item) == 1: item = item[0]
        if isinstance(item, int):
            return self.arr[item]
        elif isinstance(item, LinComb):
            if (not ignore_errors()) and (item.value < 0 or item.value >= len(self.arr)):
                raise IndexError(str(item.value)+"<0 or "+str(item.value)+">="+str(len(self.arr)))
            ixs = [item==ix for ix in range(len(self.arr))]
            sum(ixs).assert_eq(1)
            ret = lin_comb(ixs, self.arr)
            if isinstance(ret, Array): ret=ArrayRow(ret) # prevents doing a[x][y]=1 which does not work
            return ret
        elif isinstance(item, tuple):
            return self[item[0]][item[1:]]
        else:
            raise TypeError

    def __setitem__(self, item, value):
        if isinstance(item, tuple) and len(item)==1: item = item[0]
        if isinstance(item, int):
            self.arr[item] = value
        elif isinstance(item, LinComb):
            if (not ignore_errors()) and (item.value < 0 or item.value >= len(self.arr)):
                raise IndexError(str(item.value)+"<0 or "+str(item.value)+">="+str(len(self.arr)))
            ixs = [item==ix for ix in range(len(self.arr))]
            sum(ixs).assert_eq(1)
            for ix in range(len(self.arr)):
                self.arr[ix] = if_then_else(ixs[ix], value, self.arr[ix])
        elif isinstance(item, tuple):
            it = self[item[0]]
            if isinstance(it, ArrayRow): it=Array(it)
            it[item[1:]] = value
            self[item[0]] = it
        else:
            raise TypeError

    def __sub__(self, other):
        if isinstance(other, Array):
            return Array([sv-ov for (sv,ov) in zip(self.arr, other.arr)])
        
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, Array):
            return Array([sv+ov for (sv,ov) in zip(self.arr, other.arr)])
        elif is_base_value(other) or isinstance(other, LinComb):
            return Array([sv+other for sv in self.arr])
        
        return NotImplemented

    __radd__ = __add__

    def __rmul__(self, other):
        if is_base_value(other) or isinstance(other, LinComb):
            return Array([other*sv for sv in self.arr])
        
        return NotImplemented
    
    __mul__=__rmul__
    
    def __if_then_else__(self, other, cond):
        if not isinstance(other, Array):
            raise TypeError("expected Array, got " + str(other))
        return other+cond*(self-other)
    
    def assert_eq(self, other):
        if len(self.arr)!=len(other.arr):
            raise ValueError("arrays not of the same length: " + str(len(self.arr)) + "!=" + str(len(other.arr)))

        for (l,r) in zip(self.arr, other.arr): l.assert_eq(r)

    def joined(self):
        return [val for ar in self.arr for val in ar.arr]
   
class ArrayRow(Array):
    def __init__(self, arg):
        self.arr = arg.arr
    def __setitem__(self, item, value):
        raise TypeError("Cannot set value in a returned array row; use arr[a,b] or convert into array")