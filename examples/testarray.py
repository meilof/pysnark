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

from pysnark.runtime import PrivVal
from pysnark.array import Array

if __name__ == '__main__':
    # simple array demo
    arr = Array([3, 4, 5, 6])
    print("array", arr, arr[2], arr[PrivVal(2)])
    arr[2] = 1
    print("array", arr, arr[2], arr[PrivVal(2)])

    # use array as matrix

    arr = Array([Array([1, 2]), Array([3, 4]), Array([5, 6])])
    print("matrix", arr)
    print("matrix get row", arr, arr[1], arr[PrivVal(1)])
    arr[PrivVal(2)] = Array([7, 8])
    print("matrix", arr)
    
    print("get element", arr[PrivVal(1)][PrivVal(1)])
    #arr[PrivVal(1)][PrivVal(1)] = 99  # not allowed
    arr[PrivVal(1),PrivVal(1)] = 99
    arr[2,0] = 0
    print("matrix get el", arr, arr[PrivVal(1),PrivVal(1)])
    