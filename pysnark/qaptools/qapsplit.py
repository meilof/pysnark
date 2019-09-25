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

import hashlib
import sys

import pysnark.qaptools.options

def contextualize(lst):
    global context
    context = None
    def nxt(z):
        global context
        l,m,r=z.partition("/")
        if m!="":
            if context!=None and l!=context:
                raise ValueError("Inconsistent contexts: " + str(l) + " <-> " + str(context) + " in: " + str(lst))
            context=l
            return r
        return l
    ctl = list(map(nxt, lst))
    return context, ctl


eqs = dict()
blocks = dict()


def getqap(nm):
    if not nm in blocks: blocks[nm] = []
    if not nm in eqs: eqs[nm] = []

    bstr = lambda x: "[ioblock] " + x[0] + " " + " ".join(x[1])
    eqstr = lambda eq: " ".join(eq)

    return sorted(list(map(bstr, blocks[nm])) + list(map(eqstr, eqs[nm])))


def qaphash(q):
    m = hashlib.md5()
    for line in q:
        m.update(bytes(line, 'utf-8'))
    return m.hexdigest()[:10]

def qapsplit():
    """

    :return: (maximum qap size, maximum input block size) encountered
    """
    global eqs, blocks

    fns = dict()
    extblocks = set()

    schedf = open(pysnark.qaptools.options.get_schedule_file(), "w")

    for ln in open(pysnark.qaptools.options.get_eqs_file()):
        ln = ln.strip()
        if ln=="" or ln[0]=="#": continue
        toks = ln.strip().split(" ")

        if toks[0]=="[function]":
            fns[toks[2]]=toks[1]
            print("[function]", toks[2], pysnark.qaptools.options.get_eqs_file_fn(toks[1]), pysnark.qaptools.options.get_ek_file(toks[1]), pysnark.qaptools.options.get_vk_file(toks[1]), file=schedf)
            #print "function ", toks[2], toks[1]
        elif toks[0]=="[ioblock]":
            chk,lst = contextualize(toks[3:])
            if chk!=toks[1]:
                raise ValueError("Inconsistent contexts: " + chk + "<->" + toks[1])
            if not toks[1] in blocks: blocks[toks[1]]=[]
            blocks[toks[1]].append((toks[2],lst))
        elif toks[0]=="[external]":
            print(toks[0], toks[1], toks[2], pysnark.qaptools.options.get_block_file(toks[3]), pysnark.qaptools.options.get_block_comm(toks[3]), file=schedf)
            extblocks.add((toks[1],toks[2]))
        elif toks[0]=="[glue]":
            print(ln, file=schedf)
        else:
            qap, tokn = contextualize(toks)
            if not qap in eqs: eqs[qap]=[]
            eqs[qap].append(tokn)


    hexs = dict()
    
    print("*** qaptools subroutines:", file=sys.stderr)
        
    for x in fns:
        q = getqap(x)
        hs = qaphash(q)
        
        print("***    id:", x, "function:", fns[x], "digest:", hs, "#constraints:", len(eqs[x]), end=' ', file=sys.stderr)
        if fns[x] in hexs and hexs[fns[x]]!=hs:
            raise ValueError("*** Inconsistent functions: " + fns[x]+"."+hs + "<->" + fns[x]+"."+hexs[fns[x]])
        if not fns[x] in hexs:
            outf = open(pysnark.qaptools.options.get_eqs_file_fn(fns[x]), "w")
            print("\n".join(q+[]), file=outf)
            outf.close()
            hexs[fns[x]]=hs
            print("*", file=sys.stderr)
        else:
            print(".", file=sys.stderr)

    def maxperqap(nm):
        try:
            return max([len(blk[1]) for blk in blocks[nm] if (nm,blk[0]) in extblocks])
        except ValueError:
            return 0

    def ioperqap(nm):
        #print("ioperqap for ", nm, blocks[nm])  if (nm, blk[0]) in extblocks]
        try:
            return sum([len(blk[1]) for blk in blocks[nm]])
        except ValueError:
            return 0

    return dict([(fns[fn], len(eqs[fn])) for fn in fns]),\
           max([ioperqap(nm) for nm in blocks]),\
           max([maxperqap(nm) for nm in blocks]),\
           hexs


if __name__ == "__main__":
    qapsplit()
