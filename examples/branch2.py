import sys

import pysnark.runtime
from pysnark.runtime import PrivVal, LinComb, add_guard, restore_guard, igprint
from pysnark.branching import BranchingValues, if_then_else, _if, _elif, _else, _endif, _range, _while, _endwhile, _endfor, _breakif
        
_ = BranchingValues()
        
def test():
    __=BranchingValues()
    
    __.z = 40
    
    if _if(PrivVal(1)):
        __.z = 100
    if _else():
        __.z = 200
    _endif()
        
    return __.z
    
_.y=3
print("_.y", _.y)
print("_.vals", _.vals)
if _if(PrivVal(0)):
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

print("after if", _.vals)


        
done = 0
_.w=0
while _while(done!=PrivVal(5)) and done!=10:
    igprint("in while loop")
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




k = PrivVal(9)
_.sum = 0
for i in _range(k, max=9, checkstopmax=True):
    igprint("in loop")
    _breakif(i==3)
    _.sum = i
_endfor()

print("sum", _.sum)

#sys.exit(0)

print("nc", pysnark.runtime.num_constraints)
for i in _range(10, max=10):
    igprint("i")
_endfor()
print("nc", pysnark.runtime.num_constraints)

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



#print("nc", pysnark.runtime.num_constraints)


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
    _.a=10
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