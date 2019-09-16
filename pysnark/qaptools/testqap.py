# Copyright (c) 2016-2018 Koninklijke Philips N.V. All rights reserved. A
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

"""
This tool tests whether the wire file in the current location (as given by
:py:func:`pysnark.options.get_wire_file`) satisfies all equations of the
current Quadratic Arithmetic Program (as given by
:py:func:`pysnark.options.get_eqs_file`)

Run with

  python -m pysnark.testqap
"""

import pysnark.qaptools.options
from pysnark.qaptools.backend import vc_p

if __name__ == "__main__":
    vals = {}

    for ln in open(options.get_wire_file()):
      ln = ln.strip()
      if ln=="" or ln[0]=="#": continue
      (var,val) = ln.split(" ")
      var = var[:-1]
      vals[var] = int(val)

    for ln in open(options.get_io_file()):
      ln = ln.strip()
      if ln=="" or ln[0]=="#": continue
      (var,val) = ln.split(" ")
      var = var[:-1]
      vals[var] = int(val)

    def getval(v):
        if v in vals: return vals[v]
        if v.endswith("/one"): return 1

    def val(str):
        lst = str.strip().split(" ")
        return sum([int(c)*getval(v) for (c,v) in zip(lst[0::2],lst[1::2])])

    for (ix,ln) in enumerate(open(options.get_eqs_file())):
        ln = ln.strip()
        if ln[0]=="[" or ln[0]=="#": continue
        lhs,rhs = ln.split("=")
        t1,t2 = lhs.strip().split("*")
        eval = ((val(t1)%vc_p)*(val(t2)%vc_p)-val(rhs))%vc_p
        if eval!=0:
            print("*** line", (ix+1), "gave non-zero value:", eval)
            print(ln)

    print("Tested all", ix+1, "lines")
