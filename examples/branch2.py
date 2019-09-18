import pysnark.nobackend
import pysnark.runtime

from pysnark.runtime import PrivVal
from pysnark.branching import if_then_else

# TODO: support dictionary argument, give error if called from function without a dict

globs = {}

class NoContext:
    def __getattr__(self, nm):
        global globs
        print("*** getting", nm)
        return globs[nm]
    
    def __setattr__(self, nm, val):
        global globs
        print("*** setting", nm, val)
        globs[nm] = val
        
#_ = NoContext()
#
#_.a = 3
#print(_.a)

class IfContext:
    inif = True       # whether the current branch is the if branch
    vals = {}         # overwritten values
    nodefvals = set() # previous values that were not defined before the if
    
    def __init__(self, cond):
        self.cond = cond
        self.acond = 1-cond
    
    def __getattr__(self, nm):
        global globs

        if (not self.inif) and (not nm in self.vals) and (nm in self.nodefvals):
            raise ValueError("no value set for " + nm)
        
        return globs[nm]
    
    def __setattr__(self, nm, val):
        global globs
        
        # TODO: not ideal
        if nm=="inif" or nm=="vals" or nm=="nodefvals" or nm=="cond" or nm=="acond": return object.__setattr__(self, nm, val)
        
        if not nm in globs or globs[nm] is None:
            if self.inif:
                self.nodefvals.add(nm)
                globs[nm] = None
            else:
                raise ValueError("writing previously unset variable: " + nm)
        
        if not nm in self.vals: self.vals[nm] = globs[nm]
        globs[nm] = val
        
    def _finish_prev(self):
        if self.inif:
            for nm in self.vals:
                if not nm in self.nodefvals:
                    globs[nm] = if_then_else(self.cond, globs[nm], self.vals[nm])
        else:
            for nm in self.nodefvals:
                if not nm in self.vals: raise ValueError("branch did not set variable: " + nm)
            
            for nm in self.vals:
                globs[nm] = if_then_else(self.cond, globs[nm], self.vals[nm])
        
    def _elif(self, cond):
        self._finish_prev()
        self.cond = self.acond & cond
        self.acond = self.acond & (1-cond)
        self.inif = False
        self.vals = {}
        
    def _else(self):
        self._finish_prev()
        self.cond = self.acond
        self.inif = False
        self.vals = {}
        
    def _endif(self):
        self._finish_prev()
       
globs["y"]=3
_ = IfContext(PrivVal(1))
_.x = 3
_.y = 4
_._elif(PrivVal(0))
_.x = 1
_.y = 5
_._else()
_.x = 7
_._endif()

print(globs)