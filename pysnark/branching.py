# Copytight (C) Meilof Veeningen, 2019

import copy
import inspect

import pysnark.runtime

from pysnark.runtime import guarded, is_base_value, PubVal, PrivVal, ignore_errors, is_base_value, LinComb, add_guard, restore_guard
from pysnark.boolean import LinCombBool
from pysnark.fixedpoint import LinCombFxp

def if_then_else(cond, truev, falsev):
    if truev is falsev:
        return truev
    
    if isinstance(cond, int):
        if cond != 0 and cond != 1:
            raise ValueError("if_then_else can only take Boolean values")
        return truev if cond else falsev

    if not isinstance(cond, LinCombBool):
        raise RuntimeError("Wrong type for if_then_else condition")

    if callable(truev): truev = guarded(cond)(truev)()
    if callable(falsev): falsev = guarded(-cond)(falsev)()        

    if isinstance(truev, list):
        return [if_then_else(cond, truevi, falsevi) for (truevi,falsevi) in zip(truev,falsev)]
    
    if isinstance(truev, LinCombFxp):
        falsev = LinCombFxp._ensurefxp(falsev)
    return falsev + cond * (truev - falsev)

class BranchingValues:
    def __init__(self):
        self.vals = {}
        self.stack = []
        
    def __del__(self):
        if len(self.stack)>0: raise RuntimeError("unclosed branches left")

    def __getattr__(self, nm):
        if nm=="vals" or nm=="stack": return super().__getattr__(nm)
        return self.vals[nm]
    
    def __setattr__(self, nm, val):
        if nm=="vals" or nm=="stack": return super().__setattr__(nm, val)
        self.vals[nm] = val
        
    def backup(self):
        ret = {}
        for nm,val in self.vals.items():
            ret[nm] = copy.deepcopy(val)
        return ret

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
        #if not isinstance(nwcond,LinComb): nwcond = LinComb.ZERO+nwcond
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

class ObliviousIterator():
    def __init__(self, start, stop, max, ctx, checkstopmax):
        self.start = start
        self.stop = stop
        self.max = max
        self.ctx = ctx
        self.ix = None
        self.checkstopmax = checkstopmax
        
    def __next__(self):
        if self.ix is None:
            self.ix = self.start
            self.ctx.stack.append(WhileContext(self.ix!=self.stop,self.ctx))
            return self.ix
        else:
            self.ix += 1
            if (isinstance(self.stop,int) and self.ix<self.stop) or (
                not isinstance(self.stop,int) and self.ix<self.max):
                self.ctx.stack[-1]._while(self.ix!=self.stop)
                return self.ix
            else:
                if self.checkstopmax:
                    (self.ctx.stack[-1].cond&(self.ix!=self.stop)).assert_zero("stop exceeds max")
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
