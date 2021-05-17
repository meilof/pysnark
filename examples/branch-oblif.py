import sys

import pysnark.runtime
from pysnark.runtime import PrivVal
from oblif.decorator import oblif

@oblif
def test():
    z = 40
    
    if PrivVal(1):
        z = 100
    else:
        z = 200
        
    return z

print("test", test())

@oblif
def test2():
    y=3
    if PrivVal(0):
        x = 3
        if PrivVal(0):
            z = 4
        else:
            z = 5
            y = test()
    elif PrivVal(0):
        x = 1
        y = 5
        z = 10
    else:
        x = 7
        z = 2
        
    print("after if", x, y, z)
    return x,y,z
    
print("test2: ", test2())


@oblif
def test3():
    done = 0
    w=0
    while done!=PrivVal(5) and done!=10:
        w = done
        done += 1
        if done==3: break
            
test3()

@oblif
def test4():
    k = PrivVal(9)
    sum = 0
    for i in range(min(k,9)):
        if i==3: break
        sum = i
    return sum
    
print("test4", test4())

