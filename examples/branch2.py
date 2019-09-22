import copy
import inspect
import sys

#import pysnark.nobackend
import pysnark.runtime

from pysnark.runtime import PrivVal, LinComb, add_guard, restore_guard
from pysnark.branching import if_then_else

class BranchingValues:
    def __init__(self):
        self.vals = {}
        self.stack = []
        self.__setattr__ = self._setattr # override after initing the other two
        
    def __del__(self):
        if len(self.stack)>0: raise RuntimeError("unclosed branches left")

    def __getattr__(self, nm):
        return self.vals[nm]
    
    def _setattr(self, nm, val):
        self.vals[nm] = val
        
    def backup(self):
        ret = {}
        for nm,val in self.vals.items():
            ret[nm] = copy.deepcopy(val)
        return ret
        
_ = BranchingValues()

class BranchContext:
    def __init__(self, cond, ctx):
        self.ctx = ctx
        self.nodefvals = None
        self.enter(cond)
                
    def exit(self):
        restore_guard(self.origguard)
        
        if self.nodefvals is None:
            self.nodefvals = {}
            for nm in self.ctx.vals:
                if not nm in self.bak:
                    self.nodefvals[nm] = self.ctx.vals[nm]
        else:
            for nm in self.nodefvals:
                if not nm in self.ctx.vals: raise RuntimeError("branch did not set value for " + nm)
                self.nodefvals[nm] = if_then_else(self.cond, self.ctx.vals[nm], self.nodefvals[nm])
        for nm in self.nodefvals: del self.ctx.vals[nm]

        for nm in self.ctx.vals:
            if nm in self.bak:
                self.ctx.vals[nm] = if_then_else(self.cond, self.ctx.vals[nm], self.bak[nm])
            else:
                raise RuntimeError("branch set spurious value: " + nm)
        
    def enter(self, nwcond):
        self.bak = self.ctx.backup()        
        self.cond = nwcond
        self.origguard = add_guard(nwcond)
        
    def end(self):
        self.exit()

class IfContext(BranchContext):
    def __init__(self, cond, ctx):
        self.icond = 1-cond # should be before super().__init__ because may be guarded
        super().__init__(cond, ctx)
        
    def _elif(self, nwcond):
        if not callable(nwcond):
            raise ValueError("argument to _elif should be a function")
            
        self.exit()
        nwcond = nwcond()
        nwicond = self.icond&(1-nwcond) # need to calculate before entering guard
        self.enter(self.icond&nwcond)
        self.icond = nwicond
        
    def _else(self):
        self.exit()
        self.enter(self.icond)
        self.icond = None
        
    def end(self):
        super().end()
        if len(self.nodefvals)>0 and self.icond is not None:
            raise RuntimeError("if branch set " + str(list(self.nodefvals.keys())) + " and no else branch")
        else:
            for nm in self.nodefvals: self.ctx.vals[nm]=self.nodefvals[nm]
        
def getcontext(ctx):
    if ctx is not None: return ctx
    locs = inspect.currentframe().f_back.f_back.f_locals
    if "_" in locs and isinstance(locs["_"], BranchingValues):
        print("Found directly")
        return locs["_"]
    for nm in locs:
        if isinstance(locs[nm], BranchingValues):
            return locs[nm]
    raise RuntimeError("no BranchingValues instance found in locals")

#def calledfromfunction():
#    us = inspect.currentframe()
#    # if called from module: us=us, us.f_back=_if, us.f_back.f_back=module, us.f_back.f_back.f_back is None
#    # if called from function: us=us, us.f_back=_if, us.f_back.f_back=fn, us.f_back.f_back.f_back is module
#    if us is None or us.f_back is None or us.f_back.f_back is None or us.f_back.f_back.f_back is None: return False
#    return True
    
def _if(cond,ctx=None):
    ctx = getcontext(ctx)
    ctx.stack.append(IfContext(cond,ctx))
    return True

def _elif(nwcond,ctx=None):
    getcontext(ctx).stack[-1]._elif(nwcond)
    return True

def _else(ctx=None):
    getcontext(ctx).stack[-1]._else()
    return True

def _endif(ctx=None):
    getcontext(ctx).stack.pop().end()
        
def test():
    __=BranchingValues()
    
    #__.z = 40
    
    if _if(PrivVal(1), ctx=__):
        __.z = 100
    if _else():
        __.z = 200
    _endif()
        
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
    #_.z = 11
if _elif(lambda:PrivVal(0)): 
    _.x = 1
    _.y = 5
    _.z = 10
if _else():
    _.x = 7
    _.z = 2
_endif()

print(_.vals)





class WhileContext(BranchContext):
    def exit(self):
        super().exit()
        if len(self.nodefvals)>0:
            raise RuntimeError("conditional write to undefined variables: " + str(list(self.nodefvals.keys())))
    
    def _while(self, nwcond):
        self.exit()
        self.enter(self.cond&nwcond)
        
    def end(self):
        super().end()

def _while(cond,ctx=None):
    ctx = getcontext(ctx)
        
    lineno = inspect.currentframe().f_back.f_lineno
    if len(ctx.stack)!=0 and isinstance(ctx.stack[-1],WhileContext) and \
       ctx.stack[-1].ctx is ctx and ctx.stack[-1].lineno == lineno:
        ctx.stack[-1]._while(cond)
    else:
        ctx.stack.append(WhileContext(cond,ctx))
        ctx.stack[-1].lineno = lineno
    return True

def _endwhile(ctx=None):
    getcontext(ctx).stack.pop().end()
    
def _breakif(cond,ctx=None):
    getcontext(ctx).stack[-1]._while(1-cond)
        
done = 0
_.w=0
while _while(done!=PrivVal(5)) and done!=10:
    print("in while loop")
    _.w = done
    done += 1
    _breakif(done==3)
_endwhile()

#sys.exit(0)
    
_.wh = 0
_while(PrivVal(0))
_.wh = 3
_endwhile()

print("after a while", len(_.stack), _.wh, _.w)
#sys.exit(0)


class ObliviousIterator():
    def __init__(self, start, stop, max, ctx, checkstopmax):
        self.start = start
        self.stop = stop
        self.max = max
        self.ctx = ctx
        self.ix = None
        self.checkstopmax = checkstopmax
#        print("doing while", self.ix, self.stop, self.ix!=self.stop)
#        _while(self.ix!=self.stop, ctx=ctx)
        
    def __next__(self):
        if self.ix is None:
            self.ix = self.start
            self.ctx.stack.append(WhileContext(self.ix!=self.stop,self.ctx))
            return self.ix
        else:
            self.ix += 1
            if self.ix<self.max:
                self.ctx.stack[-1]._while(self.ix!=self.stop)
                return self.ix
            else:
                if self.checkstopmax:
                    (self.ctx.stack[-1].cond&(self.ix!=self.stop)).assert_zero()
                raise StopIteration
#        if self.ix==self.max:
            # make sure that ix was not >max
#            nz = (self.cond & (self.ix!=self.stop))
#            raise StopIteration

#        _breakif(self.ix==self.stop)
#        return self.ix
    
class _range:
    def __init__(self, arg1, arg2=None, max=None, ctx=None, checkstopmax=False):
        if arg2 is None:
            self.start = 0
            self.stop = arg1
        else:
            if isinstance(arg1, LinComb): raise TypeError("start cannot be private")
            self.start = arg1
            self.stop = arg2
        
        self.max = max
        
        self.ctx=getcontext(ctx)
        self.checkstopmax = checkstopmax
        
    def __iter__(self):
        return ObliviousIterator(self.start, self.stop, self.max, self.ctx, self.checkstopmax)


def _endfor(ctx=None):
    getcontext(ctx).stack.pop().end()

k = PrivVal(9)
_.sum = 0
for i in _range(k, max=9, checkstopmax=True):
    print("in loop")
    _breakif(i==3)
    _.sum = i
_endfor()

print("sum", _.sum)

#sys.exit(0)

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

_.a=PrivVal(2)

if _if(_.a<=7):
    bits = _.a.to_bits(3)
    _.a=bits[0]
_endif()
    
print("a is", _.a)

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