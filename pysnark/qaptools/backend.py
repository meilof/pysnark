    # Portions copyright (C) Meilof Veeningen 2019
#
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

# Copyright (C) Meilof Veeningen, 2019

import os
import os.path
import random as rndom
import subprocess
import sys

import pysnark.gmpy

from . import options
from .options import vc_p
from . import qapsplit
from . import runqapgen
from . import runqapinput
from . import runqapgenf
from . import runqapprove
from . import runqapver
from . import schedule

from shutil import which
if not which(options.get_qaptool_exe("qapgen")):
    raise RuntimeError("Could not find qaptools executable " + options.get_qaptool_exe("qapgen"))

random = rndom.SystemRandom()

vc_ctx = None
vc_ctr = dict()
vc_ioctr = dict()

qape = None                # qap equation file (only for key generation)
qapv = None                # qap wire value file
qapvo = None

runtime = None

def init():
    global qape, qapv, qapvo, runtime

    qapv = open(options.get_wire_file(), "w")
    print("# PySNARK wire values ", file=qapv)

    qapvo = open(options.get_io_file(), "w")
    print("# PySNARK i/o", file=qapvo)

    qape = open(options.get_eqs_file(), "w")
    print("# PySNARK equations", file=qape)
    
    import pysnark.runtime
    runtime = sys.modules["pysnark.runtime"]

def inited(fn):
    def inited_(*args, **kwargs):
        global vc_ctx
        if vc_ctx is None:
            vc_ctx = ""
            init()
            enterfn("main", "main")
        return fn(*args, **kwargs)

    return inited_

class Sig:
    def __init__(self, sig):
        self.sig = sig
        
    def __str__(self):
        """ Return string representation of linear combination represented by this VcShare. """
        return " ".join(map(lambda cv: str(cv[0])+" "+cv[1], self.sig))
    
    def __add__(self, other):
        return Sig(self.sig + other.sig)
    
    def __sub__(self, other):
        return self + (-other)
    
    def __mul__(self, other):
        return Sig([(c * other % vc_p, v) for (c, v) in self.sig])
    
    def __neg__(self):
        return Sig([(-c % vc_p, v) for (c, v) in self.sig])

@inited
def privval(val):
    vc_ctr[vc_ctx] += 1
    sid = vc_ctx + "/" + str(vc_ctr[vc_ctx])
    printwire(val, sid)
    return Sig([(1,sid)])

@inited
def pubval(val):
    vc_ctr[vc_ctx] += 1
    sid = vc_ctx + "/" + str(vc_ctr[vc_ctx])
    printwire(val, sid)

    vc_ioctr[vc_ctx] += 1
    sido = vc_ctx + "/o_" + str(vc_ioctr[vc_ctx])
    printwireout(val, sido)

    print("*", "= 1", sid, "-1", sido, file=qape)
    qape.flush()
    
    return Sig([(1,sid)])

def zero():
    return Sig([])
    
@inited
def one():
    return Sig([(1, vc_ctx+"/onex")])

def fieldinverse(val):
    return int(pysnark.gmpy.invert(val, vc_p))

def get_modulus():
    return vc_p

@inited
def add_constraint(v, w, y):
    print(v, "*", w, "=", y, ".", file=qape)    
    
@inited
def prove():
    try:
        qaplens,blklen,extlen,sigs = qapsplit.qapsplit()

        #print("qaplens", qaplens, "blklen", blklen, "extlen", extlen, "sigs", sigs)
        if extlen is None: extlen = 0
        if blklen is None: blklen = 0

        sz = 1<<((max([max(qaplens.values()),blklen,extlen])-1).bit_length())
        pubsz = 1<<((extlen-1).bit_length()) if extlen is not None else 0
        #print("qaplen:", max(qaplens.values()), "blklen:", blklen, "extlen:", extlen, "sz", sz, "pubsz", pubsz)

        cursz, curpubsz = runqapgen.ensure_mkey(sz, pubsz)

        for nm in list(sigs.keys()):
            runqapgenf.ensure_ek(nm, sigs[nm], 1<<((qaplens[nm]-1).bit_length()))

        runqapprove.run()

        allfs = list(schedule.oftype("function"))
        (eqs,eks,vks) = list(map(set,list(zip(*[(fn[1], fn[2], fn[3]) for fn in allfs])))) if allfs!=[] else (set(),set(), set())
        alles = list(schedule.oftype("external"))
        (wrs,cms) = list(map(set,list(zip(*[(fn[2], fn[3]) for fn in alles])))) if alles!=[] else (set(),set())

        if os.path.isfile(options.get_mpkey_file()) and all([os.path.isfile(vk) for vk in vks]):
            vercom = runqapver.run()
            print("*** verification succeeded", file=sys.stderr)
        else:
            vercom = runqapver.getcommand()
            print("*** verification keys missing, skipping verification", file=sys.stderr)

        print("***  prover keys/eqs: ", options.get_mkey_file(), " ".join(eks), " ".join(eqs), options.get_schedule_file(), file=sys.stderr)
        print("***  prover data:     ", " ".join(wrs), file=sys.stderr)
        print("***  verifier keys:   ", options.get_mpkey_file(), " ".join(vks), options.get_schedule_file(), file=sys.stderr)
        print("***  verifier data:   ", " ".join(cms), options.get_proof_file(), options.get_io_file(), file=sys.stderr)
        print("***  verifier cmd:    ", vercom, file=sys.stderr)
        if cursz>sz or curpubsz>pubsz:
            print("*** Evaluation/public keys larger than needed for function: " +\
                                str(cursz)+">"+str(sz) + " or " + str(curpubsz)+">"+str(pubsz)+ ".", file=sys.stderr)
            print("*** To re-create, remove " + options.get_mkey_file() + " and " +\
                                options.get_mpkey_file() + " and run again.", file=sys.stderr)

        #print >>sys.stderr, "  key material + proof material:"
        #print >>sys.stderr, " ", options.get_mpkey_file(), vks,\
        #                    options.get_schedule_file(), , bcs
    except RuntimeError as rr:
        print("*** Error in qaptools: " + str(rr), file=sys.stderr)

@inited
def printwire(sh, nm):
    if qapv is not None:
        print(nm+":", sh, file=qapv)
        qapv.flush()

@inited
def printwireout(sh, nm):
    if qapvo is not None:
        print(nm+":", sh, file=qapvo)
        qapvo.flush()

def enterfn(fname, call=None):
    """
    Start a new call of the given function type
    :param fname: Function name. All instances of the same function should execute the exact same sequence of instructions
    :param call: Call name. Should be globally unique (autogenerated if not given)
    :return: Call name
    """

    global vc_ctx, vc_ctr, vc_ioctr

    if vc_ctx is None: init()

    if call is None:
        call=(vc_ctx+"_"+str(vc_ctr[vc_ctx])+"_" if vc_ctx is not None else "") + fname

    if qape!=None: print("[function]", fname, call, file=qape)
    
    vc_ctx = call
    vc_ctr[vc_ctx] = 0
    vc_ioctr[vc_ctx] = 0

    printwire(random.randint(0, vc_p-1), call+"/deltav") 
    printwire(random.randint(0, vc_p-1), call+"/deltaw")
    printwire(random.randint(0, vc_p-1), call+"/deltay")

    printwire(1, call + "/onex")
    if qape!=None:
        print("* = 1 " + call + "/one -1 " + call + "/onex", file=qape)

    return call


@inited
def continuefn(call):
    """
    Continue execution of the given function call
    :param call: Function call
    :return: None
    """
    global vc_ctx, vc_ctr
    vc_ctx = call
    vc_ctr[vc_ctx] += 1


def for_each_in(cls, f, struct):
    """ Recursively traversing all lists and tuples in struct, apply f to each
        element that is an instance of cls. Returns structure with f applied. """
    if isinstance(struct, list):
        return [for_each_in(cls, f, x) for x in struct]
    elif isinstance(struct, tuple):
        return tuple([for_each_in(cls, f, x) for x in struct])
    else:
        if isinstance(struct, cls):
            return f(struct)
        else:
            return struct

@inited
def vc_declare_block(bn, vcs, rnd1=None):
    global vc_ctx, vc_ctr
    
    def ensure_single(x):
        if len(x.lc.sig)==1: return x
            
        ret = runtime.PrivVal(x.value)
        ret.assert_eq(x)
        return ret

    vcs = [ensure_single(x) for x in vcs]
    if rnd1 is None: rnd1 = random.randint(0, vc_p-1)
    printwire(rnd1, vc_ctx+"/rnd1_"+bn)
    printwire(random.randint(0, vc_p-1), vc_ctx+"/rnd2_"+bn)

    if qape is not None:
        print("[ioblock]", vc_ctx, bn, " ".join([x.lc.sig[0][1] for x in vcs]), file=qape)
        qape.flush()

    return vcs

@inited
def importcomm(bn, nm=None):
    global vc_ctr, vc_ctx
    if nm is None:
        nm = str(vc_ctr[vc_ctx])
        vc_ctr[vc_ctx] += 1

    fl = options.get_block_file(bn)
    if not os.path.isfile(fl):
        raise IOError("Wire file " + fl + " for imported block \"" + bn + "\" does not exist")
    vals = [int(ln.strip()) for ln in open(fl)]
    vvals = vc_declare_block(nm, [runtime.PrivVal(val) for val in vals[:-1]], vals[-1])

    if qape is not None:
        print("[external]", vc_ctx, nm, bn, file=qape)
        qape.flush()

    return vvals

@inited
def exportcomm(vals, bn, nm=None):
    global vc_ctr, vc_ctx
    if nm is None:
        nm = str(vc_ctr[vc_ctx])
        vc_ctr[vc_ctx] += 1

    valsp = [val if isinstance(val, runtime.LinComb) else runtime.PrivVal(val) for val in vals]

    rnd = random.randint(0,vc_p-1)
    vc_declare_block(nm, valsp, rnd)
    
    runqapinput.writecomm(bn, [val.value for val in valsp], rnd)
    runqapgen.ensure_mkey(-1, len(vals))
    runqapinput.run(bn)

    if qape is not None:
        print("[external]", vc_ctx, nm, bn, file=qape)
        qape.flush()

    return valsp


def vc_glue(ctx1, ctx2, vals):
    global vc_ctx, vc_ctr

    bakctx = vc_ctx

    rndv = random.randint(0, vc_p - 1)

    vc_ctx = ctx1
    bn1 = str(vc_ctr[vc_ctx])
    vc_ctr[vc_ctx] += 1
    vc_declare_block(bn1, [x[0] for x in vals], rndv)

    vc_ctx = ctx2
    bn2 = str(vc_ctr[vc_ctx])
    vc_ctr[vc_ctx] += 1
    vc_declare_block(bn2, [x[1] for x in vals], rndv)

    vc_ctx = bakctx

    if qape!=None:
        print("[glue]", ctx1, bn1, ctx2, bn2, file=qape)
        qape.flush()


def subqap(nm):
    def subqap_(fn):
        @inited
        def subqap__(*args, **kwargs):
            global vc_ctx

            if kwargs: raise ValueError("@subqap-decorated functions cannot have keyword arguments")

            oldctx = vc_ctx
            call = enterfn(nm)
            newctx = vc_ctx

            argret = []

            def copyandadd(el):
                ret = runtime.PrivVal(el.value)
                argret.append((el, ret))
                return ret

            def copyandaddrev(el):
                ret = runtime.PrivVal(el.value)
                argret.append((ret, el))
                return ret

            argscopy = for_each_in(runtime.LinComb, copyandadd, args)
            ret = fn(*argscopy, **kwargs)
            continuefn(oldctx)
            retcopy = for_each_in(runtime.LinComb, copyandaddrev, ret)

            vc_glue(oldctx, newctx, argret)

            return retcopy

        return subqap__

    return subqap_
    

#
#
#def prove():
#
#
#
#    @classmethod
#    def vars(cls, vals, nm, dim=1):
#        ln = len(str(len(vals)-1))
#        caller = cls if dim==1 else lambda val,nm: cls.vars(val,nm, dim-1)
#        return [caller(val, (nm+"_"+str(ix).zfill(ln))) for (ix,val) in enumerate(vals)]
#
#    @classmethod
#    def vals(cls, vars, nm):
#        ln = len(str(len(vars)-1))
#        return [var.val(nm+"_"+str(ix).zfill(ln)) for (ix,var) in enumerate(vars)]
#
#    def strsig(self):
#
#    def __repr__(self):
#        """ Return string representation of this VcShare. """
#        val = self.value if self.value < vc_p/2 else self.value-vc_p
#        return "{" + str(val) + "}"
#        #return "VcShare(" + self.strsig() + (":"+str(self.sh.result) if hasattr(self.sh, 'result') else "") + ")"
#
#    #@inited
#    def ensure_single(self):
#        """ Return a VcShare with the same value that is guaranteed to refer
#            to one witness, by making a new VcShare and adding the required
#            equation if necessary. """
#        if len(self.sig)==1 and self.sig[0][0]==1: return self
#        
#        ret = Var(self.value, True)
#        if qape!=None:
#            print >>qape, "*", "=", self.strsig(), "-1", ret.sig[0][1]
#            qape.flush()
#            
#        return ret
#    
#    @classmethod
#    def zero(cls):
#        """ Return a VcShare representing the value zero. """
#        
#    
#    @classmethod
#    @inited
#    def constname(self):
#        return vc_ctx + "/onex"
#    
#    @classmethod
#    def constant(cls, val):
#        """ Return a VcShare representing the given constant value. """
#        return Var(val, [(val % vc_p, cls.constname())])
#
#    @classmethod
#    def random(cls):
#        """ Return a VcShare representing a random value. """
#        return cls(random.randint(0, vc_p-1))
#
#    @classmethod
#    def tovar(cls, val, nm=None):
#        if isinstance(val, Var): return val
#        return Var(val, nm)
#
#    @inited
#    def val(self, nm=None):
#        global vc_ctx, vc_ctr
#        Var(self.value, nm)
#        return self.value
#
#    def __neg__(self):
#        """ Returns negated VcShare. """
#        return Var(vc_p - self.value, [(-c % vc_p, v) for (c, v) in self.sig])
#        
#    def __add__(self, other):
#        """ Add VcShare or constant to self. """
#        if other==0: return self
#        if isinstance(other,int) or isinstance(other,long):
#            return Var((self.value + other) % vc_p, self.sig + [(other, self.constname())])
#        elif isinstance(other, Var):
#            return Var((self.value + other.value) % vc_p, self.sig + other.sig)
#        else:
#            raise TypeError("unsupported operand type(s) for VcShare.+: '{}' and '{}'".format(self.__class__, type(other)))
#    __radd__ = __add__
#            
#    def __sub__(self, other):
#        """ Subtract VcShare or constant from self. """
#        if isinstance(other,int) or isinstance(other,long):
#            return Var((self.value - other) % vc_p, self.sig + [(-other, self.constname())])
#        elif isinstance(other, Var):
#            return self+(-other)
#        else:
#            raise TypeError("unsupported operand type(s) for VcShare.-: '{}' and '{}'".format(self.__class__, type(other)))
#            
#    def __rsub__(self, other):
#        return -self + other
#    
#    def __mul__(self, other):
#        """ Multiply VcShare with other VcShare or constant. """
#        
#        if isinstance(other,int) or isinstance(other,long):
#            return Var((self.value * other) % vc_p, [(c * other % vc_p, v) for (c, v) in self.sig])
#        elif isinstance(other, Var):
#            res = Var((self.value * other.value) % vc_p, True)
#            vc_assert_mult(self, other, res)
#            return res
#        else:
#            return NotImplemented
#
#    __rmul__ = __mul__
#
#    def assert_zero(self):
#        """ Assert that the present VcShare represents the value zero. """
#        if self.value!=0: raise ValueError("nonzero value " + str(self.value))
#
#        if qape!=None:
#            print >>qape, "* =", self.strsig(), "."
#            qape.flush()
#
#    def assert_equals(self, other):
#        (self-other).assert_zero()
#            
#    def assert_nonzero(self):
#        if self.value==0: raise ValueError("zero value")
#
#        inv = Var(long(invert(self.value, vc_p)), True)
#        vc_assert_mult(self, inv, Var.constant(1))
#        
#    def assert_bit(self):
#        """
#        Assert that this variable contains a bit, i.e., 0 or 1
#        :return: None
#        """
#
#        if self.value!=0 and self.value!=1: raise ValueError(str(self.value) + " is not a bit")
#        vc_assert_mult(self, 1 - self, Var.zero())
#            
#    def bit_decompose(self, bl):
#        """ Assert that the present VcShare represents a positive value, that
#            is, a value in [0,2^bl] with bl the given bit length. """
#            
#        bits = [Var((self.value & (1 << i)) >> i, True) for i in xrange(bl)]
#        for i in xrange(len(bits)): vc_assert_mult(bits[i], 1 - bits[i], Var.zero())
#        vc_assert_mult(Var.zero(), Var.zero(), self - sum([(2 ** i) * bits[i] for i in xrange(len(bits))]))
#        return bits
#
#    assert_positive = bit_decompose
#
#    def __div__(self, other):
#        if isinstance(other,int) or isinstance(other,long):
#            otherv = long(invert(other%vc_p, vc_p))
#            return self*otherv
#        else:
#            raise TypeError("unsupported operand type(s) for VcShare./: '{}' and '{}'".format(self.__class__, type(other)))
#
#    def divmod(self, divisor, maxquotbl):
#        """
#        Divide by public value and return quotient and remainder
#        :param divisor: Divisor (integer)
#        :param maxquotbl: Maximal bitlength of the resulting quotient
#        :return: Quotient and remainder
#        """
#        quo = Var(self.value/divisor, True)
#        rem = Var(self.value-quo.value*divisor, True)
#
#        rem.assert_smaller(divisor)
#        quo.assert_positive(maxquotbl)
#
#        (self-divisor*quo-rem).assert_zero()
#        return [quo,rem]
#        
#    def assert_smaller(self, val):
#        if self.value>=val: raise ValueError("value too large: " + str(self.value) + ">=" + str(val))
#        self.bit_decompose(val.bit_length())
#        (val-1-self).bit_decompose(val.bit_length())
#
#    def isnonzero(self):
#        """ Returns VcShare equal to 1 if self is not zero, and 0 if self is zero. """
#
#        eqzs = 1 if self.value != 0 else 0
#        ret = Var(eqzs, True)
#        
#        m = Var(long(invert(self.value + (1 - ret.value), vc_p)), True)
#        
#        if qape!=None:
#            vc_assert_mult(self, m, ret)
#            vc_assert_mult(self, Var.constant(1) - ret, Var.zero())
#                
#        return ret
#
#    def iszero(self):
#        return 1-self.isnonzero()
#
#    def equals(self, other):
#        return (self-other).iszero()
