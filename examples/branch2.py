import copy

import pysnark.nobackend
import pysnark.runtime

from pysnark.runtime import PrivVal, LinComb
from pysnark.branching import if_then_else

class BranchingContext:
    vals = {}
    baks = {}

    def __getattr__(self, nm):
        if not nm in self.vals:
            raise KeyError("variable not defined: " + nm)
        elif isinstance(self.vals[nm], int) or isinstance(self.vals[nm], LinComb):
            # immutable objects: return
            return self.vals[nm]
        else:  
            # todo: deep copy/copy on write
            raise TypeError("incorrect type: " + nm)
    
    def __setattr__(self, nm, val):
        if not nm in self.baks:
            self.baks[nm] = self.vals[nm] if nm in self.vals else None
        
        self.vals[nm] = val
        
    def conditional_update(self, cond):
        for nm in self.baks:
            if not self.baks[nm] is None:
                self.vals[nm] = if_then_else(cond, self.vals[nm], self.baks[nm])
        
_ = BranchingContext()

# ("if",ctx,(icond,cond,nodefvals,bakbak))
__cond_stack = []

def _if(cond,ctx=None):
    if ctx is None: ctx = _
    __cond_stack.append(("if",ctx,(1-cond,cond,None,ctx.baks)))
    ctx.baks.clear()
    return True

def _ifelse_update():
    (_if,ctx,(icond,cond,nodefvals,bakbak)) = __cond_stack[-1]
    if _if!="if": raise RuntimeError("_elseif used in context of " + _if)
        
    if nodefvals is None:
        nodefvals = {}
        # exiting the if branch, check which values are newly written
        for nm in ctx.baks:
            if ctx.baks[nm] is None:
                nodefvals[nm] = ctx.vals[nm]
                del ctx.vals[nm]
    else:
        for nm in nodefvals:
            if not nm in ctx.baks: raise RuntimeError("branch did not set value for " + nm)
            nodefvals[nm] = if_then_else(cond, ctx.vals[nm], nodefvals[nm])
            del ctx.vals[nm]
    
    __cond_stack[-1] = (_if,ctx,(icond,cond,nodefvals,bakbak))
    ctx.conditional_update(cond)
    ctx.baks.clear()

def _elif(nwcond):
    _ifelse_update()
    (_if,ctx,(icond,_,nodefvals,bakbak)) = __cond_stack[-1]
    __cond_stack[-1] = (_if,ctx,(icond&(1-nwcond),icond&nwcond,nodefvals,bakbak))
    return True

def _else():
    _ifelse_update()
    (_if,ctx,(icond,_,nodefvals,bakbak)) = __cond_stack[-1]
    __cond_stack[-1] = (_if,ctx,(None,icond,nodefvals,bakbak))
    return True

def _endif():
    _ifelse_update()
    (_,ctx,(icond,_,nodefvals,bakbak))=__cond_stack.pop()
    if len(nodefvals)>0 and icond is not None: raise RuntimeError("if branch set " + str(nodefvals) + " and no else branch")
    ctx.baks.update(bakbak)
    for nm in nodefvals: setattr(ctx,nm,nodefvals[nm])
    
_.y=3
if _if(PrivVal(1)):
    _.x = 3
    if _if(PrivVal(1)):
        _.z = 4
    if _else():
        _.z = 5
    _endif()
    _.y = 4
if _elif(PrivVal(1)):
    _.x = 1
    _.y = 5
    _.z = 10
if _else():
    _.x = 7
    _.z = 2
_endif()

print(_.vals)

