# Copytight (C) Meilof Veeningen, 2019

import pysnark.uselibsnark


backend=pysnark.uselibsnark

"""
Operating principles:
 - if wrong type of value is given as argument, raise ValueError or
   NotImplemented
 - if wrong values are given:
     - if ignore_errors is given, proceed and generate the same constraints
       as normal (use add_constraint_unsafe for constraints that will still
       always hold and add_constraint otherwise)
     - otherwise, raise ValueError or AssertionError
"""
ignore_errors=False

""" Bitlength for bitwise operations. Values are signed values between -2^(bitlength-1) and 2^(bitlength-1) """
bitlength=16

def is_base_value(obj): return isinstance(obj, int)

def assert_base_value(obj):
    if not is_base_value(obj):
        raise TypeError("value " + obj + " has unsupported type " + type(obj))

def add_constraint_unsafe(v, w, y):
    backend.add_constraint(v.lc, w.lc, y.lc)

"""
If set, all constraints added via do_add_constraint will be guarded by this guard,
meaning that if guard.value==1, they should be satfiesfied and if guard.value==0,
a dummy value will be added to satisfy them
"""
guard = None

""" Add constraint v*w=y to the constraint system, and update running computation hash. """
def add_constraint(v,w,y):
    if not guard is None:
        dummy = PrivVal(v.value*w.value-y.value)
        add_constraint_unsafe(v,w,y+dummy)
        add_constraint_unsafe(guard,dummy,LinComb.zero())
    else:
        if v.value*w.value!=y.value:
            # note that we do the check over the integers
            if ignore_errors: raise ValueError("Constraint did not hold")
            
        add_constraint_unsafe(v,w,y)

class LinComb:
    def __init__(self, value, lc):
        self.value = value
        self.lc = lc   
    
    def __repr__(self):
        return "{" + str(self.value) + "}"
    
    # self<other, so other-self>0, so other-self-1>=0
    def __lt__(self, other): return (other-self-1).check_positive()
    def assert_lt(self, other): (other-self-1).assert_positive()
        
    # self<=other, so other-self>=0
    def __le__(self, other): return (other-self).check_positive()
    def assert_le(self, other): (other-self).assert_positive()
    
    def __eq__(self, other): return (self-other).check_zero()
    def assert_eq(self, other): (self-other).assert_zero()
        
    def __ne__(self, other): return 1-(self==other)
    def assert_ne(self, other): (self-other).assert_nonzero()
        
    # self>other, so self-other>0, so self-other-1>=0
    def __gt__(self, other): return (self-other-1).check_positive()
    def assert_gt(self, other): (self-other-1).assert_positive()
        
    # self>=other, so self-other>=0
    def __ge__(self, other): return (self-other).check_positive()
    def assert_ge(self, other): (self-other).assert_positive()
        
    def __bool__(self):
        raise NotImplementedError("Should not run bool() on a LinComb")
        
    def __add__(self, other):
        if isinstance(other, LinComb):
            return LinComb(self.value+other.value, self.lc+other.lc)
        elif is_base_value(other):
            return self + other*ONE
        else:
            return NotImplemented
        
    def __sub__(self, other):
        return self+(-other)
    
    def __mul__(self, other):
        if isinstance(other, LinComb):
            retval = PubVal(self.value*other.value)
            add_constraint_unsafe(self, other, retval)
            return retval
        elif is_base_value(other):
            return LinComb(self.value*other, self.lc*other)
        else:
            return NotImplemented
                    
    def __matmul__(self, other): return NotImplemented
    
    def __truediv__(self, other): 
        """ Proper division """
        if isinstance(other, LinComb):
            if self.value % other.value != 0:
                raise ValueError(str(self.value) + " is not properly divisible by " + str(other.value))
            res = PrivVal(self.value/other.value)
            do_add_constraint(other, res, self)
            return res
        elif is_base_value(other):
            if self.value % other != 0:
                raise ValueError(str(self.value) + " is not properly divisible by " + str(other))
            return LinComb(self.value/other, self.lc*backend.fieldinverse(other))
        else:
            return NotImplemented
         
    def __floordiv__(self, other):
        """ Division with rounding """
        return self.__divmod__(other)[0]

    def __mod__(self, other):
        if divisor&(divisor-1)==0:
            # this is faster for powers of two
            return LinComb.from_bits(self.to_bits()[:divisor.bit_length()])
        
        return self.__divmod__(other)[1]
        
    def __divmod__(self, divisor):
        """ Division by public value """
        
        if not is_base_value(divisor): return NotImplemented
        
        if divisor==0: raise ValueError("division by zero")
        
        quo = PrivVal(self.value//divisor)
        rem = PrivVal(self.value-quo.value*divisor)
 
        rem.assert_positive(divisor.bit_length())
        if divisor&(divisor-1)!=0: rem.assert_lt(divisor) # not needed for powers of two
        quo.assert_positive()
        (self-divisor*quo-rem).assert_zero()
        
        return (quo,rem)
    
    def __pow__(self, other, mod=None):
        """ Exponentiation with public integral power p>=0 """
        if mod!=None: raise ValueError("cannot provide modulus")
        if not is_base_value(other): return NotImplemented
        if other<0: raise ValueError("exponent cannot be negative", other)
        if other==0: return ONE
        if other==1: return self
        return self*pow(self, other-1)
    
    def __lshift__(self, other):
        """ Left-shift with public value """
        # TODO: extend to secret offset?
        if not is_base_ovalue(other): return NotImplemented
        return self*(1<<other)
    
    def __rshift__(self, other):
        """ Right-shift with public value """
        # TODO: extend to secret offset?
        if not is_base_ovalue(other): return NotImplemented
        return LinComb.from_bits(self.to_bits[other:])
    
    def _check_both_bits(self, other):
        if ignore_errors: return
        
        if self.value !=0 and self.value!=1: raise ValueError("not a bit: " + str(self.value))
            
        if isinstance(other, LinComb) and (other.value==0 or other.value==1): return
        if is_base_value(other) and (other==0 or other==1): return
        raise ValueError("not a bit: " + str(other))
    
    def __and__(self, other):
        """ Bitwise and &. Cost: 1 constraint """
        self._check_both_bits(other)
        return self * other

    def __xor__(self, other):
        """Bitwise exclusive-or ^. Cost: 1 constraint """
        self._check_both_bits(other)
        return self + other - 2 * self * other

    def __or__(self, other):
        """Bitwise or |. Cost: 1 constraint """
        self._check_both_bits(other)
        return self + other - self * other

    __radd__ = __add__

    def __rsub__(self, other):
        return other+(-self)
    
    __rmul__ = __mul__
    
    def __rmatmul__(self, other): return NotImplemented

    def __rtruediv__(self, other):
        """ Proper division by LinComb """
        if not is_base_value(other): return NotImplemented
        
        if other % self.value != 0:
            raise ValueError(str(other.value) + " is not properly divisible by " + str(self.value))
            
        res = PrivVal(other/self.value)
        do_add_constraint(self, res, other*ONE)
        return res
        
    def __rfloordiv__(self, other): return NotImplemented
    def __rmod__(self, other): return NotImplemented
    def __rdivmod__(self, other): return NotImplemented
    def __rpow__(self, other): return NotImplemented
    def __rlshift__(self, other): return NotImplemented
    def __rrshift__(self, other): return NotImplemented

    __rand__ = __and__
    __rxor__ = __xor__
    __ror__ = __or__

    def __neg__(self):
        return LinComb(-self.value, -self.lc)
    
    def __pos__(self):
        return self
    
    def __abs__(self):
        from .branching import if_then_else
        return if_then_else(self>=0, self, -self)

    def __invert__(self):
        # we do not want to do ~1=0 and ~0=1 since this is also not true for native ints
        raise NotImplementedError("Operator ~ not supported; for binary not, use 1-x")
        
    def __complex__(self): return NotImplemented
    def __int__(self): raise NotImplementedError("Should not run int() on LinComb")
    def __float__(self): return NotImplemented
    
    def __round__(self, ndigits=None): return NotImplemented
    def __trunc__(self): return NotImplemented
    def __floor__(self): return NotImplemented
    def __ceil__(self): return NotImplemented

    def assert_bool(self):
        add_constraint(self, 1-self, ZERO)

    def assert_bool_unsafe(self):
        add_constraint_unsafe(self, 1-self, ZERO)
        
    def to_bits(self, bits=bitlength):
        if (not ignore_errors) and (self.value<0 or self.value.bit_length()>bits):
            raise ValueError("value " + str(self.value) + " is not a " + str(bits) + "-bit positive integer")
            
        bits = [PrivVal((self.value&(1<<ix))>>ix) for ix in range(bits)]
        for bit in bits: bit.assert_bool_unsafe()
            
        (self-LinComb.from_bits(bits)).assert_zero()
        
    @classmethod
    def from_bits(cls, bits):
        return sum([biti*(1<<i) for (i,biti) in enumerate(bits)])
        
    """
    Given a value in [-1<<bitlength,1>>bitlength], check if it is positive.
    Note that this works on (bitlength+1)-length values so it works for
    __lt__, etc on bitlength-length values
    """
    def check_positive(self, bits=bitlength):
        if (not ignore_errors) and self.value.bit_length()>bits:
            raise ValueError("value " + str(self.value) + " is not a " + str(bits) + "-bit integer")
            
        ret = PrivVal(1 if self.value>=0 else 0)
        abs = self.value if self.value>=0 else -self.value
        
        bits = [PrivVal((abs&(1<<ix))>>ix) for ix in range(bits)]
        for bit in bits: bit.assert_bool_unsafe()
            
        # if ret==1, then requires that 2*self=self+sum, so sum=self
        # if ret==0, this requires that 0=self+sum, so sum=-self
        add_constraint(2*ret, self, self+LinComb.from_bits(bits))
        
        return ret
            
    def assert_positive(self, bits=bitlength):
        self.to_bits(bits)
        
    def check_zero(self):
        ret = PrivVal(1 if self.value==0 else 0)
        
        wit = PrivVal(backend.fieldinverse(self.value+ret.value))  # add ret.value so always nonzero
        
        # Trick from Pinocchio paper: if self is zero then ret=1 by first eq,
        # if self is nonzero then ret=0 by second eq
        add_constraint_unsafe(self, wit, 1-ret)
        add_constraint_unsafe(self, ret, ZERO)
        
        return ret
    
    def assert_zero(self):
        if (not ignore_errors) and self.value!=0:
            raise ValueError("Value " + str(self.value) + " is not zero")
            
        add_constraint(ZERO, ZERO, self)        
            
    def assert_nonzero(self):
        if (not ignore_errors) and self.value==0:
            raise ValueError("Value " + str(self.value) + " is not zero")
            
        wit = PrivVal(backend.fieldinverse(self.value if self.value!=0 else 1))
        add_constraint(self, wit, ONE)
    
ZERO = LinComb(0, backend.zero())
ONE = LinComb(1, backend.one())        

def PubVal(val):
    return LinComb(val, backend.pubval(val))

def PrivVal(val):
    return LinComb(val, backend.privval(val))

def for_each_in(cls, f, struct):
    """ Recursively traversing all lists and tuples in struct, apply f to each
        element that is an instance of cls. Returns structure with f applied. """
    if isinstance(struct, list):
        return list(map(lambda x: for_each_in(cls, f, x), struct))
    elif isinstance(struct, tuple):
        return tuple(map(lambda x: for_each_in(cls, f, x), struct))
    else:
        if isinstance(struct, cls):
            return f(struct)
        else:
            return struct

"""
Turns the given function into a SNARK. Input and outputs to the function are
converted to public SNARK inputs (via PubVal). Input/output conversion is also
performed over lists and tuples, but not over more complex objects.

Can be used as a decorator, e.g., 

>>> pysnark.runtime.snark(lambda x: x*x*x)(3)
9
"""
def snark(fn):
    def snark__(*args, **kwargs):
        if kwargs: raise ValueError("@snark-decorated functions cannot have keyword arguments")

        argscopy = for_each_in(int, lambda x: PubVal(x), args)
        ret = fn(*argscopy, **kwargs)
        retcopy = for_each_in(LinComb, lambda x: x.val(), ret)

        return retcopy
        
    return snark__

#+def snark(fn):
#+    def snark__(*args, **kwargs):
#+        if kwargs: raise ValueError("@snark-decorated functions cannot have keyword arguments")
# 
#-            argscopy = for_each_in(Var, copyandadd, args)
#-            ret = fn(*argscopy, **kwargs)
#-            continuefn(oldctx)
#-            retcopy = for_each_in(Var, copyandaddrev, ret)
#+        argscopy = for_each_in(int, lambda x: PubVal(x), args)
#+        ret = fn(*argscopy, **kwargs)
#+        retcopy = for_each_in(LinComb, lambda x: x.val(), ret)
# 
#-            vc_glue(oldctx, newctx, argret)
#+        return retcopy
#+        
#+    return snark__
# 
#-            return retcopy
#+""" Running hash of the constraint system, used to check whether key material should be rebuilt. """
# 
#-@inited
#-def vc_assert_mult(v,w,y):
#-    """ Add QAP equation asserting that v*w=y. """
#-    if (v.value*w.value-y.value)%vc_p!=0:
#-        if not options.ignore_errors: raise ValueError("QAP equation did not hold")
#+def is_base_value(obj):
#+    return isinstance(obj, int)
# 
#-    if qape!=None:
#-        print >>qape, v.strsig(), "*", w.strsig(), "=", y.strsig(), "."
#-        qape.flush()
#-        
#-class Var:
#-    """ A variable of the verifiable computation """
#-    @inited
#-    def __init__(self, val, sig=None):
#+def assert_base_value(obj):
#+    if not is_base_value(obj):
#+        raise TypeError("value " + obj + " has unsupported type " + type(obj))
#+    
#+class LinComb:
#+    """ A variable of the SNARK computation """
#+    def __init__(self, val, sig):
#         """ Constructor.
#-
#-        If sig is None, this is an I/O variable with an automatic label.
#-        If sig is a string, this is an I/O variable with a given name.
#-        If sig is True, this is an internal variable with an automatic label.
#-        If sig is anything else, the signature is set to this value.
#+        
#+        Val is the value
#+        Sig is a list of (coef,ix), where coef is a coefficient and ix is an
#+        index of a variable of the SNARK. ix=0 denotes the constant value one.
#+        Positive indices correspond to witnesses and public values.
#         """
#-        global vc_ctx, vc_ctr, vc_ioctr
#-
#-        self.value = val % vc_p
#-
#-        if sig==None or sig==True or isinstance(sig, str) or isinstance(sig, unicode):
#-            vc_ctr[vc_ctx] += 1
#-            sid = vc_ctx + "/" + str(vc_ctr[vc_ctx])
#-            printwire(val, sid)
#-            self.sig = [(1,sid)]
#-
#-            if sig!=True:
#-                if sig==None:
#-                    vc_ioctr[vc_ctx] += 1
#-                    sido = vc_ctx + "/o_" + str(vc_ioctr[vc_ctx])
#-                else:
#-                    sido = vc_ctx + "/o_" + sig
#-
#-                printwireout(val, sido)
#-
#-                if qape != None:
#-                    print >> qape, "*", "= 1", sid, "-1", sido
#-                    qape.flush()
#-        else:
#-            self.sig = sig
#+        
#+        self.value = val
#+        self.sig = sig
# 
#         if len(self.sig)>100:
#-            vc_ctr[vc_ctx] += 1
#-            sid = vc_ctx + "/" + str(vc_ctr[vc_ctx])
#-            printwire(val, sid)
#-
#-            if qape!=None:
#-                print >>qape, "*", "=", self.strsig(), "-1", sid
#-                qape.flush()
#-
#-            self.sig = [(1,sid)]
#-
#-    @classmethod
#-    def vars(cls, vals, nm, dim=1):
#-        ln = len(str(len(vals)-1))
#-        caller = cls if dim==1 else lambda val,nm: cls.vars(val,nm, dim-1)
#-        return [caller(val, (nm+"_"+str(ix).zfill(ln))) for (ix,val) in enumerate(vals)]
#-
#-    @classmethod
#-    def vals(cls, vars, nm):
#-        ln = len(str(len(vars)-1))
#-        return [var.val(nm+"_"+str(ix).zfill(ln)) for (ix,var) in enumerate(vars)]
#-
#-    def strsig(self):
#-        """ Return string representation of linear combination represented by this VcShare. """
#-        return " ".join(map(lambda (c,v): str(c)+" "+v, self.sig))
#+            # this is to prevent extremely long constraints, which are
#+            # inefficient for the Python runtime to handle
#+            tmp = PrivVal(val)
#+            
#+            # cannot compute self-tmp because this would again have
#+            # len(self.sig>0), causing an endless loop
#+            self.value = 0
#+            self.sig.extend((-tmp).sig)
#+            self.assert_zero()
#+            
#+            self.value = val
#+            self.sig = tmp.sig
# 
#+    def __bool__(self):
#+        raise NotImplementedError("Cannot convert LinComb to bool (are you trying to branch on a secret variable?)")
#+    
#     def __repr__(self):
#         """ Return string representation of this VcShare. """
#-        val = self.value if self.value < vc_p/2 else self.value-vc_p
#-        return "{" + str(val) + "}"
#-        #return "VcShare(" + self.strsig() + (":"+str(self.sh.result) if hasattr(self.sh, 'result') else "") + ")"
#-
#-    #@inited
#-    def ensure_single(self):
#-        """ Return a VcShare with the same value that is guaranteed to refer
#-            to one witness, by making a new VcShare and adding the required
#-            equation if necessary. """
#-        if len(self.sig)==1 and self.sig[0][0]==1: return self
#-        
#-        ret = Var(self.value, True)
#-        if qape!=None:
#-            print >>qape, "*", "=", self.strsig(), "-1", ret.sig[0][1]
#-            qape.flush()
#-            
#-        return ret
#-    
#+        return "{" + str(self.value) + "}"
#+
#     @classmethod
#     def zero(cls):
#-        """ Return a VcShare representing the value zero. """
#-        return Var(0, [])
#-    
#-    @classmethod
#-    @inited
#-    def constname(self):
#-        return vc_ctx + "/onex"
#+        """ Return a VcShare representing the value zero. Cost: none """
#+        return LinComb(0, [])
#     
#     @classmethod
#     def constant(cls, val):
#-        """ Return a VcShare representing the given constant value. """
#-        return Var(val, [(val % vc_p, cls.constname())])
#-
#+        """ Return a VcShare representing the given constant value. Cost: none """
#+        assert_base_value(val)
#+        return LinComb(val, [(val, 0)])
#+    
#     @classmethod
#-    def random(cls):
#-        """ Return a VcShare representing a random value. """
#-        return cls(random.randint(0, vc_p-1))
#+    def one(cls):
#+        """ Return constant one. Cost: none """
#+        return cls.constant(1)
# 
#-    @classmethod
#-    def tovar(cls, val, nm=None):
#-        if isinstance(val, Var): return val
#-        return Var(val, nm)
#-
#-    @inited
#-    def val(self, nm=None):
#-        global vc_ctx, vc_ctr
#-        (self-Var(self.value, nm)).assert_zero()
#+    def val(self):
#+        """ Creates a SNARK output for the current output, and return its value. Cost: 1 constraint """
#+        (self-PubVal(self.value)).assert_zero()
#         return self.value
#-
#-    def __neg__(self):
#-        """ Returns negated VcShare. """
#-        return Var(vc_p - self.value, [(-c, v) for (c, v) in self.sig])
#-        
#+ 
#     def __add__(self, other):
#-        """ Add VcShare or constant to self. """
#-        if other==0: return self
#-        if isinstance(other,int) or isinstance(other,long):
#-            return Var((self.value + other) % vc_p, self.sig + [(other, self.constname())])
#-        elif isinstance(other, Var):
#-            return Var((self.value + other.value) % vc_p, self.sig + other.sig)
#+        """ Add other LinComb or constant value. Cost: none """
#+        if isinstance(other, LinComb):
#+            return LinComb(self.value + other.value, self.sig + other.sig)
#+        elif is_base_value(other):
#+            if other==0: return self
#+            return LinComb(self.value + other, self.sig + [(other, 0)])
#         else:
#-            raise TypeError("unsupported operand type(s) for VcShare.+: '{}' and '{}'".format(self.__class__, type(other)))
#+            return NotImplemented
#+        
#     __radd__ = __add__
#-            
#+    
#     def __sub__(self, other):
#-        """ Subtract VcShare or constant from self. """
#-        if isinstance(other,int) or isinstance(other,long):
#-            return Var((self.value - other) % vc_p, self.sig + [(-other, self.constname())])
#-        elif isinstance(other, Var):
#+        """ Subtract other LinComb or constant value. Cost: none"""
#+        if isinstance(other, LinComb):
#             return self+(-other)
#+        elif is_base_value(other):
#+            if other==0: return self
#+            return LinComb(self.value - other, self.sig + [(-other, 0)])
#         else:
#-            raise TypeError("unsupported operand type(s) for VcShare.-: '{}' and '{}'".format(self.__class__, type(other)))
#-            
#+            return NotImplemented
#+    
#     def __rsub__(self, other):
#         return -self + other
#     
#     def __mul__(self, other):
#-        """ Multiply VcShare with other VcShare or constant. """
#-        
#-        if isinstance(other,int) or isinstance(other,long):
#-            return Var((self.value * other) % vc_p, [(c * other % vc_p, v) for (c, v) in self.sig])
#-        elif isinstance(other, Var):
#-            res = Var((self.value * other.value) % vc_p, True)
#-            vc_assert_mult(self, other, res)
#+        """ Multiply with other LinComb (cost: 1 constraint) or constant (cost: none) """
#+        if isinstance(other, LinComb):
#+            res = PrivVal(self.value * other.value)
#+            do_add_constraint_unsafe(self, other, res)
#             return res
#+        elif is_base_value(other):
#+            return LinComb(self.value * other, [(c*other, v) for (c, v) in self.sig])
#         else:
#             return NotImplemented
#-
#+        
#     __rmul__ = __mul__
#-
#-    def assert_zero(self):
#-        """ Assert that the present VcShare represents the value zero. """
#-        if self.value!=0: 
#-            if not options.ignore_errors: raise ValueError("nonzero value " + str(self.value))
#-
#-        if qape!=None:
#-            print >>qape, "* =", self.strsig(), "."
#-            qape.flush()
#-
#-    def assert_equals(self, other):
#-        (self-other).assert_zero()
#-            
#-    def assert_nonzero(self):
#-        if self.value==0: 
#-            if not options.ignore_errors: raise ValueError("zero value")
#-
#-        inv = Var(long(invert(self.value if self.value!=0 else 1, vc_p)), True)
#-        vc_assert_mult(self, inv, Var.constant(1))
#+    
#+    def __matmul__(self, other):
#+        return NotImplemented
#+    
#+    def __rmatmul__(self, other):
#+        return NotImplemented
#+    
#+    def __truediv__(self, other):
#+        """
#+        Proper division by public value (cost: free) or private value (cost: 1 constraint)
#+        TODO: This can have unexpected semantics if the division is not proper. Should probably add check.
#+        :param other: Value to divide by. A ValueError is raised if the division is not proper
#+        """
#+        if isinstance(other, LinComb):
#+            if self.value % other.value != 0:
#+                raise ValueError(str(self.value) + " is not properly divisible by " + str(other.value))
#+            res = PrivVal(self.value/other.value)
#+            do_add_constraint(other, res, self)
#+            return res
#+        elif is_base_value(other):
#+            if self.value % other != 0:
#+                raise ValueError(str(self.value) + " is not properly divisible by " + str(other))
#+            return LinComb(self.value/other, [(libsnark.fdiv(c,other), v) for (c, v) in self.sig])
#+        else:
#+            return NotImplemented
#         
#-    def assert_bit(self):
#+    def __rtruediv__(self, other):
#+        """
#+        Perform proper division of public value (cost: free) or private value (cost: 1 constraint)
#+        TODO: This can have unexpected semantics if the division is not proper. Should probably add check.
#+        :param other: Value to divide by the current value. A ValueError is raised if the division is not proper
#+        """
#+        
#+        # TODO: does this work?
#+        
#+        if is_base_value(other): other = LinComb.constant(other)
#+        if not isinstance(other, LinComb): return NotImplemented
#+        
#+        if other.value % self.value != 0:
#+            raise ValueError(str(other.value) + " is not properly divisible by " + str(self.value))
#+        res = PrivVal(other.value/self.value)
#+        do_add_constraint(self, res, other)
#+        return res         
#+        
#+    def __floordiv__(self, other):
#         """
#-        Assert that this variable contains a bit, i.e., 0 or 1
#-        :return: None
#+        Division with rounding ('//'). Cost: see __divmod__
#         """
#+        return self.__divmod__(other)[0]
#+    
#+    def __rfloordiv__(self, other):
#+        return NotImplemented
#+    
#+    def __mod__(self, other):
#+        """ Modulo. Cost: see __divmod__ """
#+        return self.__divmod__(other)[1]
#+    
#+    def __rmod__(self, other):
#+        return NotImplemented
#+        
#+    def __divmod__(self, divisor):
#+        """
#+        Divide by public value and return tuple (quotient,remainder)
#+        :param divisor: divisor
#+        :return: Quotient and remainder
#+        
#+        Quotient should have at most pysnark.options.bitlength bits
#+        Cost: TODO: compute
#+        """
#+        
#+        if not is_base_value(divisor): return NotImplemented
#+        
#+        quo = PrivVal(self.value//divisor)
#+        rem = PrivVal(self.value-quo.value*divisor)
# 
#-        if self.value!=0 and self.value!=1:
#-            if not options.ignore_errors: raise ValueError(str(self.value) + " is not a bit")
#-        vc_assert_mult(self, 1 - self, Var.zero())
#-            
#-    def bit_decompose(self, bl):
#+        rem.assert_positive(divisor.bit_length())
#+        rem.assert_lt(divisor)
#+        quo.assert_positive()
#+
#+        (self-divisor*quo-rem).assert_zero()
#+        return (quo,rem)
#+    
#+    def __rdivmod__(self, other):
#+        return NotImplemented
#+    
#+    def __pow__(self, other):
#         """ 
#-        Determines a bit decomposition of the given value with the given bit
#-        length, with least significant bit first.
#+        Exponentiation with public integral power p>=0. Cost: p-1 constraints
#+        """
#+        if not is_base_value(other): return NotImplemented
#+        if other<0: raise ValueError("Exponent cannot be negative", other)
#+        if other==0: return LinComb.constant(1)
#+        if other==1: return self
#+        return self*pow(self, other-1)
#+    
#+    def __rpow__(self, other):
#+        return NotImplemented
#+    
#+    def __lshift__(self, other):
#+        """
#+        Left-shift with public value. Cost: none
#         """
#+        # TODO: extend to secret offset?
#+        if not is_base_ovalue(other): return NotImplemented
#+        return self*(1<<other)
#+    
#+    def __rlshift__(self, other):
#+        return NotImplemented
#+    
#+    def __rshift__(self, other):
#+        """
#+        Right-shift with public value. Cost: pysnark.options.bitlength+1 constraints
#+        """
#+        # TODO: extend to secret offset?
#+        if not is_base_ovalue(other): return NotImplemented
#+        
#+        if other<0 or other>options.bitlength:
#+            raise ValueError("Cannot shift by " + str(other) + " bits (bitlength=" + options.bitlength + ")")
#             
#-        bits = [Var((self.value & (1 << i)) >> i, True) for i in xrange(bl)]
#-        for i in xrange(len(bits)): vc_assert_mult(bits[i], 1 - bits[i], Var.zero())
#-        vc_assert_mult(Var.zero(), Var.zero(), self - sum([(2 ** i) * bits[i] for i in xrange(len(bits))]))
#-        return bits
#+        bits = self.to_bits()
#+        return sum([(2 ** i) * bits[i+other] for i in range(len(bits)-other)])
#+    
#+    def __rrshift__(self, other):
#+        return NotImplemented
#+    
#+    def _check_both_bits(self, other):
#+        if self.value !=0 and self.value!=1:
#+            raise ValueError("Cannot perform bitwise operation on non-bit " + str(self.value))
#+            
#+        if isinstance(other, LinComb):
#+            if other.value!=0 and other.value!=1:
#+                raise ValueError("Cannot perform bitwise operation on non-bit " + str(other.value))
#+        elif is_base_value(other):
#+            if other!=0 and other!=1:
#+                raise ValueError("Cannot perform bitwise operation on non-bit " + str(other))
#+        else:
#+            raise ValueError("Expected bit, got " + type(other))
# 
#-    """
#-    Assert that the present VcShare represents a positive value, that is, a
#-    value in [0,2^bl] with bl the given bit length.
#-    """
#-    assert_positive = bit_decompose
#+    
#+    def __and__(self, other):
#+        """ Bitwise and &. Cost: 1 constraint """
#+        self._check_both_bits(other)
#+        return self * other
# 
#-    def __div__(self, other):
#-        if isinstance(other,int) or isinstance(other,long):
#-            otherv = long(invert(other%vc_p, vc_p))
#-            return self*otherv
#-        else:
#-            raise TypeError("unsupported operand type(s) for VcShare./: '{}' and '{}'".format(self.__class__, type(other)))
#+    __rand__ = __and__
# 
#-    def divmod(self, divisor, maxquotbl):
#-        """
#-        Divide by public value and return quotient and remainder
#-        :param divisor: Divisor (integer)
#-        :param maxquotbl: Maximal bitlength of the resulting quotient
#-        :return: Quotient and remainder
#-        """
#-        quo = Var(self.value/divisor, True)
#-        rem = Var(self.value-quo.value*divisor, True)
#+    def __xor__(self, other):
#+        """Bitwise exclusive-or ^. Cost: 1 constraint """
#+        self._check_both_bits(other)
#+        return self + other - 2 * self * other
# 
#-        rem.assert_smaller(divisor)
#-        quo.assert_positive(maxquotbl)
#+    __rxor__ = __xor__
# 
#-        (self-divisor*quo-rem).assert_zero()
#-        return [quo,rem]
#+    def __or__(self, other):
#+        """Bitwise or |. Cost: 1 constraint """
#+        self._check_both_bits(other)
#+        return self + other - self * other
#+
#+    __ror__ = __or__ 
#+    
#+    def __neg__(self):
#+        """ Returns negated value. Cost: none """
#+        return LinComb(-self.value, [(-c, v) for (c, v) in self.sig])
#+    
#+    def __pos__(self):
#+        """ Returns value. Cost: none """
#+        return self
#+    
#+    def __abs__(self):
#+        """ Return absolute value. Cost: Cost: 3+pysnark.options.bitlength constraints """
#+        from .lib.base import if_then_else
#+        return if_then_else(self>=0, self, -self)
#+    
#+    def __invert__(self):
#+        """Bitwise not (inversion) ~. Cost: none """
#+        if self.value !=0 and self.value!=1:
#+            raise ValueError("Cannot perform bitwise operation on non-bit " + str(self.value))
#         
#-    def assert_smaller(self, val):
#-        """
#-        Assert that this secret value is strictly smaller than the given value.
#-        If it is enough to check that the value has at most a certain bitlength,
#-        it is more efficient to use bit_decompose.
#+        return 1 - self
#+    
#+    def isnonzero(self):
#+        """ Returns 1 if not equal to zero, and 0 otherwise. Cost: 2 constraints """
#+        ret = PrivVal(1 if self.value != 0 else 0)
#+        m = PrivVal(libsnark.fieldinverse(self.value + (1 - ret.value)))
#         
#-        :param val Val to compare to
#-        :return: None
#-        """
#-        if self.value>=val: 
#-            if not options.ignore_errors: raise ValueError("value too large: " + str(self.value) + ">=" + str(val))
#-        self.bit_decompose(val.bit_length())
#-        (val-1-self).bit_decompose(val.bit_length())
#+        do_add_constraint_unsafe(self, m, ret)
#+        do_add_constraint_unsafe(self, LinComb.constant(1) - ret, LinComb.zero())
#+                
#+        return ret
# 
#-        
#-    def check_smaller(self, val, maxbl):
#+    def iszero(self):
#+        """ Returns 1 if equal to zero, and 0 otherwise. Cost: 2 constraints """
#+        return 1-self.isnonzero()
#+    
#+    
#+    def __lt__(self, other):
#         """
#-        Checks if self is strictly smaller than the public/private value "val",
#-        returning 1 if this is the case and 0 if not. Both self and "val"
#-        should have bitlength "maxbl" at most
#-        :param val    Constant/private variable to compare to
#-        :param maxbl  Maximum bitlength if self and val
#-        :return:      Private variable equal to 1 if self<val and 0 otherwise
#+        Checks if self is strictly smaller than the public/private value other,
#+        returning 1 if this is the case and 0 if not. Both self and other
#+        should have bitlength pysnark.options.bitlength at most
#+        :param other  Constant/private variable to compare to
#+        :return:      Private variable equal to 1 if self<other and 0 otherwise
#+        
#+        Cost: 2+pysnark.options.bitlength constraints
#         """
#         
#-        vval = (val.value if isinstance(val,Var) else val)
#+        vval = (other.value if isinstance(other,LinComb) else other)
#         
#-        if vval.bit_length()>maxbl:
#-                if not options.ignore_errors: raise ValueError("val is longer than max bitlength: " + str(val) + ">=" + str(maxbl))
#-                
#-                
#-        if self.value.bit_length()>maxbl:
#-                if not options.ignore_errors: raise ValueError("self.value is longer than max bitlength: " + str(self.value) + ">=" + str(maxbl))
#-                    
#         if self.value < vval:
#-            cmp = Var(1, True)
#+            cmp = PrivVal(1)
#             valtocheck = vval-1-self.value       # if cmp==1 this will be >=0
#         else:
#-            cmp = Var(0, True)
#-            valtocheck = self.value-vval         # if cmp==0 this will be >=    
#+            cmp = PrivVal(0)
#+            valtocheck = self.value-vval         # if cmp==0 this will be >=
#             
#+        if valtocheck.bit_length()>options.bitlength:
#+            if not options.ignore_errors: raise ValueError("comparison between " + str(self) + " and " + str(other) + " does not fit into bitlength " + str(options.bitlength))
# 
#         # compute cmp and assert that it is a bit
#         cmp.assert_bit()
#         
#         #compute bits b1,...,bn that are a bit decomposition of B-x if x<=B and of x-B-1 if x>B.
#         # This bit decompositon would need to be max(bitlength(B),bitlengh(x)) bits lomg
#-        bits = [Var((valtocheck & (1 << i)) >> i, True) for i in xrange(maxbl)]
#+        bits = [PrivVal((valtocheck & (1 << i)) >> i) for i in range(options.bitlength)]
#         for bit in bits: bit.assert_bit()
#         
#         # assert that cmp*(2x-2bitsum(b1,..,bn)-1)+bitsum(b1,...,bn)-x+B+1 is equal to zero
#-        bitsum = sum([(2 ** i) * bits[i] for i in xrange(len(bits))])
#-        vc_assert_mult(cmp, 2*val-2*self-1,val+bitsum-self)
#+        bitsum = sum([(2 ** i) * bits[i] for i in range(len(bits))])
#+        do_add_constraint(cmp, 2*other-2*self-1,other+bitsum-self)
#         
#         return cmp
#+        
#+    def __le__(self, other):
#+        return self<(other+1)
#+
#+    def __eq__(self, other):
#+        if is_base_value(other) and other==0:
#+            return self.iszero()
#+        else:
#+            return (self-other)==0
#+        
#+    def __ne__(self, other):
#+        if is_base_value(other) and other==0:
#+            return self.isnonzero();
#+        else:
#+            return (self-other)!=0
#+
#+    def __gt__(self, other):
#+        return (-self)<(-other)
#     
#-    def isnonzero(self):
#-        """ Returns VcShare equal to 1 if self is not zero, and 0 if self is zero. """
#+    def __ge__(self, other):
#+        return (-self)<=(-other)
#+    
#+    def assert_zero(self):
#+        """ Assert that the present VcShare represents the value zero. Cost: 1 constraint """
#+        if self.value!=0: 
#+            if not options.ignore_errors: raise AssertionError("nonzero value " + str(self.value))
#+                
#+        do_add_constraint(LinComb.zero(), LinComb.zero(), self)
#+            
#+    def assert_nonzero(self):
#+        """ Assert that value is nonzero. Cost: 1 constraint """
#+        if self.value==0: 
#+            if not options.ignore_errors: raise AssertionError("zero value")
# 
#-        eqzs = 1 if self.value != 0 else 0
#-        ret = Var(eqzs, True)
#+        inv = PrivVal(libsnark.fieldinverse(self.value))
#+        do_add_constraint(self, inv, LinComb.constant(1))
#         
#-        m = Var(long(invert(self.value + (1 - ret.value), vc_p)), True)
#+    def to_bits(self, bl=None):
#+        """
#+        Determine bit dcomposition into bl (default: pysnark.options.bitlength) bits, starting with least significant bit
#         
#-        if qape!=None:
#-            vc_assert_mult(self, m, ret)
#-            vc_assert_mult(self, Var.constant(1) - ret, Var.zero())
#-                
#-        return ret
#+        Cost: bl+1 constraints
#+        """
#+        if bl is None: bl = options.bitlength
#+        
#+        if self.value<0 or self.value>=(1<<bl):
#+            if not options.ignore_errors: raise AssertionError(str(self.value) + " is too large for bitlength " + str(bl))
#+            
#+        bits = [PrivVal((self.value & (1 << i)) >> i) for i in range(bl)]
#+        
#+        do_add_constraint(LinComb.zero(), LinComb.zero(), self - sum([(2 ** i) * bits[i] for i in range(len(bits))]))
#+        for i in range(len(bits)):
#+            # TODO: do with assert_bit_safe()
#+            do_add_constraint_unsafe(bits[i], 1 - bits[i], LinComb.zero())
#+        
#+        return bits
#+    
#+    @classmethod
#+    def from_bits(cls, bits):
#+        return sum([(1<<ix)*v for (ix,v) in enumerate(bits)])
#+    
#+    """
#+    Assert that value (max bitlength: pysnark.options.bitlength) is positive,
#+    in other words, 0<=self<2^(pysnark.optiona.bitlength)
#+    
#+    Cost: pysnark.options.bitlength+1 constraints
#+    """
#+    assert_positive = to_bits
#+        
#+    def assert_bit(self):
#+        """ Assert that value is a bit. Cost: 1 constraint """
# 
#-    def iszero(self):
#-        """ Returns VcShare equal to 1 if self is zero, and 0 if self is not zero. """
#-        return 1-self.isnonzero()
#+        if self.value!=0 and self.value!=1:
#+            if not options.ignore_errors: raise AssertionError(str(self.value) + " is not a bit")
#+        do_add_constraint(self, 1 - self, LinComb.zero())
#+        
#+    def assert_lt(self, other):
#+        """
#+        Assert that self<other
#+        
#+        :param val: value to compare to (can be constant or non-constant)
#+        :return: None    
#+        Cost: 2L constraints, where L=pysnark.options.bitlength if val is not
#+        a constant and bitlength(val) otherwise. If a rough bound is enough,
#+        assert_positive is cheaper.
#+        """
#+        if isinstance(other,LinComb):
#+            val=other.value
#+        else:
#+            assert_base_value(other)
#+            val=other
#+        
#+        if self.value>=val: 
#+            if not options.ignore_errors: raise AssertionError("value too large: " + str(self.value) + ">=" + str(val))
#+
#+        (other-1-self).assert_positive(val.bit_length() if isinstance(other,int) else None)        
#+        
#+    def assert_le(self, other):
#+        """ Assert that self<=other. Cost: see assert_lt """
#+        self.assert_lt(other+1)
#+        
#+    def assert_eq(self, other):
#+        """ Assert that self is equal to other. Cost: 1 constraint """
#+        (self-other).assert_zero()
#+
#+    def assert_ne(self, other):
#+        """ Assert that self is not equal to other. Cost: 1 constraint """
#+        (self-other).assert_nonzero()
#+        
#+    def assert_gt(self, other):
#+        """
#+        Assert that self>other. Cost: see assert_lt
#+        """
#+        if isinstance(other,LinComb):
#+            val=other.value
#+        else:
#+            assert_base_value(other)
#+            val=other
#+            
#+        if self.value<=val: 
#+            if not options.ignore_errors: raise AssertionError("value too small: " + str(self.value) + ">=" + str(val))
#+
#+        (self-1-other).assert_positive(val.bit_length() if isinstance(other,int) else None)             
#+            
#+    def assert_ge(self, other):
#+        (self+1).assert_gt(other)    
#+
#+def PubVal(value):
#+    """ Defines a new SNARK input/output """
#+    varix = libsnark.add_pubval(value)
#+
#+    global comphash
#+    comphash = hash((comphash,varix))
#+    
#+    return LinComb(value, [(1,varix)])
#+
#+def PrivVal(value):
#+    """ Defines a new SNARK witness """
#+    return LinComb(value, [(1,libsnark.add_privval(value))])
# 
#-    def equals(self, other):
#-        """ Returns VcShare equal to 1 if self equals other, and 0 if self does not equal other. """
#-        return (self-other).iszero()
#+if 'sphinx' not in sys.modules and options.do_prove:
#+    import atexit
#+    from .atexitmaybe import maybe
#+    from .prove import prove
#+    atexit.register(maybe(prove))