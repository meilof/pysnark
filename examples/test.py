# from __future__ import print_function

import inspect
import sys

from pysnark.runtime import snark, PrivVal, LinComb

from pysnark.branching import if_then_else, guarded, _if, _ifelse, _elseif, _else, _while


origgi = list.__getitem__

def my_getitem(self, key):
    print(key)
    return origgi(self, key)

list.__getitem__ = origgi

lst=[2,3,4]
print(lst[2])

sys.exit(0)

#print(PrivVal(31387)>>3)

#x=PrivVal(10)
#print(if_then_else(x<8,lambda:x.to_bits(3)[0],lambda:PrivVal(33)))
#print(if_then_else((x==10)|(x==11),lambda:10,lambda:(x*x*x)))
#sys.exit()

max=PrivVal(int(sys.argv[1]))
        
guard=PrivVal(3)
out=PrivVal(2)

# if statement, without globals
@_if(guard==2)
def _(_ = {"out":out}):
    #global out
    print("Setting out")
    _["out"] = 3
print("Out of test.py", _["out"])
    
pow=PrivVal(3)
j=1
# for statement
@_while
def _():
    global j
    for i in range(10):
        j=j*2
        z=if_then_else(j<8,lambda:j.to_bits(3)[0],0)
        yield i!=max
        
print("computed power", j)

pow=PrivVal(3)
# for statement
@_while
def _(_ = {"j":PrivVal(1)}):
    for i in range(10):
        _["j"]=_["j"]*2
        z=if_then_else(j<8,lambda:_["j"].to_bits(3)[0],0)
        yield i!=max
        
print("computed power", _["j"])

sval=PrivVal(int(sys.argv[2]))
arr=[1,2,3,4,5]
ret=0
# switch statement
@_ifelse(sval==0)
def _():
    global ret
    ret=arr[0]
@_elseif(sval==1)
def _():
    global ret
    ret=arr[1]
@_elseif(lambda: sval==2)
def _():
    global ret
    ret=arr[2]
@_elseif(sval==3)
def _():
    global ret
    ret=arr[3]
@_else
def _():
    global ret
    ret=5
    
print("finally, ret is", ret)
    

sval=PrivVal(int(sys.argv[2]))
arr=[1,2,3,4,5]
ret=0
# switch statement
@_ifelse(sval==0)
def _(_={"ret":0}):
    _["ret"]=arr[0]
@_elseif(sval==1)
def _():
    _["ret"]=arr[1]
@_elseif(lambda: sval==2)
def _():
    _["ret"]=arr[2]
@_elseif(sval==3)
def _():
    _["ret"]=arr[3]
@_else
def _():
    _["ret"]=5
    
print("now, ret is", _["ret"])    
    
i=0
j=PrivVal(2)
k=-1
@_while
def _():
    global i,j
    for i in range(10):
        i=i+1
        j=j*2
        z=if_then_else(j<8,lambda:j.to_bits(3)[0],0)
        yield i!=max
    
print("done, j now", j)

@snark
def cube(x):
    y = if_then_else((x==10)|(x==11),10,x*x*x)
    return if_then_else(y>50,50,y)

print("cube-cube of 2", cube(cube(2)))

if len(sys.argv) < 2:
    print("*** Usage: ", sys.argv[0], "val")
    sys.exit(2)
    
print("The cube of 10 is", cube(10))
print("The cube of", sys.argv[1], "is", cube(int(sys.argv[1])))

for i in range(-3,3):
    for j in range(-3,3):
        print(str(i).zfill(3),"<", str(j).zfill(3),":",PrivVal(i)< PrivVal(j),end=' ')
        print(str(i).zfill(3),"<=",str(j).zfill(3),":",PrivVal(i)<=PrivVal(j),end=' ')
        print(str(i).zfill(3),">", str(j).zfill(3),":",PrivVal(i)> PrivVal(j),end=' ')
        print(str(i).zfill(3),">=",str(j).zfill(3),":",PrivVal(i)>=PrivVal(j),end=' ')
        print(str(i).zfill(3),"==",str(j).zfill(3),":",PrivVal(i)==PrivVal(j),end=' ')
        print(str(i).zfill(3),"!=",str(j).zfill(3),":",PrivVal(i)!=PrivVal(j),end=' ')
        print()