import copy
import inspect

import pysnark.nobackend
import pysnark.runtime

from pysnark.runtime import PrivVal, LinComb
from pysnark.branching import if_then_else

class BranchingContext:
    def __init__(self):
        self.vals = {}

    def __getattr__(self, nm):
        return self.vals[nm]
    
    def __setattr__(self, nm, val):
        if nm=="vals": return super().__setattr__(nm,val)
        self.vals[nm] = val
        
    def backup(self):
        ret = {}
        for nm,val in self.vals.items():
            ret[nm] = copy.deepcopy(val)
        return ret
        
_ = BranchingContext()

__ifstack = []

class IfContext:
    def __init__(self, cond, ctx):
        self.ctx = ctx
        self.icond = 1-cond
        self.cond = cond
        self.nodefvals = None
        self.bak = ctx.backup()
        
    def update(self):
        if self.nodefvals is None:
            # finializing "if" branch"
            self.nodefvals = {}
            for nm in self.ctx.vals:
                if not nm in self.bak:
                    self.nodefvals[nm] = self.ctx.vals[nm]
        else:
            # finalizing other branch
            for nm in self.nodefvals:
                if not nm in self.ctx.vals: raise RuntimeError("branch did not set value for " + nm)
                self.nodefvals[nm] = if_then_else(self.cond, self.ctx.vals[nm], self.nodefvals[nm])

        for nm in self.nodefvals: del self.ctx.vals[nm]

        for nm in self.ctx.vals:
            if nm in self.bak:
                self.ctx.vals[nm] = if_then_else(self.cond, self.ctx.vals[nm], self.bak[nm])
                
        self.bak = self.ctx.backup()

def calledfromfunction():
    us = inspect.currentframe()
    # if called from module: us=us, us.f_back=_if, us.f_back.f_back=module, us.f_back.f_back.f_back is None
    # if called from function: us=us, us.f_back=_if, us.f_back.f_back=fn, us.f_back.f_back.f_back is module
    if us is None or us.f_back is None or us.f_back.f_back is None or us.f_back.f_back.f_back is None: return False
    return True
    
def _if(cond,ctx=None):
    if ctx is None:
        if calledfromfunction(): raise RuntimeError("should provide context if calling from function")
        ctx = _
    __ifstack.append(IfContext(cond,ctx))
    return True

def _elif(nwcond):
    cur = __ifstack[-1]
    cur.update()
    cur.cond = cur.icond&nwcond
    cur.icond = cur.icond&(1-nwcond)
    return True

def _else():
    cur = __ifstack[-1]
    cur.update()
    cur.cond = cur.icond
    cur.icond = None
    return True

def _endif():
    cur = __ifstack.pop()
    cur.update()
    if len(cur.nodefvals)>0 and cur.icond is not None: raise RuntimeError("if branch set " + str(cur.nodefvals) + " and no else branch")
    for nm in cur.nodefvals: cur.ctx.vals[nm]=cur.nodefvals[nm]
        
        
def test():
    __=BranchingContext()
    
    print(id(_.vals))
    print(id(__.vals))
    print("before _", _.vals)
    
    __.z = 40
    
    if _if(PrivVal(1), ctx=__):
        __.z = 100
    if _else():
        __.z = 200
    _endif()
        
    print("after _", _.vals)
    return __.z
    
    
_.y=3
if _if(PrivVal(1)):
    _.x = 3
    if _if(PrivVal(0)):
        _.z = 4
    if _else():
        _.z = 5
    _endif()
    _.y = test()
if _elif(PrivVal(1)):
    _.x = 1
    _.y = 5
    _.z = 10
if _else():
    _.x = 7
    _.z = 2
_endif()

print(_.vals)

_forstack = []

class ObliviousIterator():
    cond = 1

    def __init__(self, start, stop, max, ctx):
        self.ix = start
        self.stop = stop
        self.max = max
        self.ctx = ctx
        self.bak = ctx.backup()
        self.cond = (self.ix!=self.stop)
        _forstack.append(self)
        
    def update(self):
        for nm in self.ctx.vals:
            if nm in self.bak:
                self.ctx.vals[nm] = if_then_else(self.cond, self.ctx.vals[nm], self.bak[nm])
            else:
                raise RuntimeError("range conditional wrote to unset variable " + nm)

        self.bak = self.ctx.backup()
        
    def __next__(self):
        self.update()
        
        self.ix += 1
        if self.ix==self.max:
            # make sure that ix was not >max
            nz = (self.cond & (self.ix!=self.stop))
            if isinstance(nz,LinComb): 
                nz.assert_zero()
            else:
                assert nz==0
            raise StopIteration
            
        self.cond = self.cond & (self.ix!=self.stop)
        return self.ix
    
class _range:
    def __init__(self, arg1, arg2=None, max=None, ctx=None):
        if arg2 is None:
            self.start = 0
            self.stop = arg1
        else:
            if isinstance(arg1, LinComb): raise TypeError("start cannot be private")
            self.start = arg1
            self.stop = arg2
        
        self.max = max
        
        if ctx is None:
            if calledfromfunction(): raise RuntimeError("should provide context if calling from function")
            ctx = _
        self.ctx = ctx
        
    def __iter__(self):
        return ObliviousIterator(self.start, self.stop, self.max, self.ctx)

def _breakif(cond):
    cur = _forstack[-1]
    
    cur.update()
    cur.cond = cur.cond&(1-cond)
    
    
#    self.cond = self.cond & cond

def _endfor():
    _forstack.pop()

k = PrivVal(9)
_.sum = 0
for i in _range(3, k, max=9):
#    _breakif(i==3)
    _.sum = i
_endfor()

print("sum", _.sum)

#print("nc", pysnark.runtime.num_constraints)
#for i in _range(10, max=10):
#    print("i")
#print("nc", pysnark.runtime.num_constraints)

_.l=[0]*4
_.l[0]=PrivVal(0)
_.l[1]=PrivVal(-1)
if _if(PrivVal(1)):
    #print("nc", pysnark.runtime.num_constraints)
    _.l[1]=1
    _.l[2]=2
#    print("nc", pysnark.runtime.num_constraints)
_endif()
print(_.l)
#print("nc", pysnark.runtime.num_constraints)



print("nc", pysnark.runtime.num_constraints)


class Tester:
    def __init__(self,a,b):
        self.a = a
        self.b = b
        
    def __if_then_else__(self,other,cond):
        return Tester(if_then_else(cond,self.a,other.a), if_then_else(cond,self.b,other.b))
        
_.tester = Tester(1,2)

if _if(PrivVal(0)):
    _.tester.a = 10
_endif()

print(_.tester.a)


#    if inspect.getargspec(fn).defaults is not None:
#        freturns = inspect.getargspec(fn).defaults[0]
#    else:
#        freturns = None
#    fglobs = inspect.getclosurevars(fn).globals
#    fmod = inspect.getmodule(fn)
#    gen=fn()
#    guard = next(gen)
#        
#    try:
#        while True:
#            cond = _if(guard, returns = freturns, globmod=fmod, globvars=fglobs)(lambda: next(gen))
#            guard = guard*cond
#    except StopIteration:
#        pass
#    
#    return freturns    