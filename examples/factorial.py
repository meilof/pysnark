# Copyright (C) Meilof Veeningen

from pysnark.runtime import PrivVal, LinComb, benchmark
from pysnark.branching import BranchingValues, if_then_else, _range, _endfor, _breakif

FAC_TEST = 5
FAC_MAX = 10

def factorial_if_comparison(n):
    ret = 1
    
    for i in range(2,FAC_MAX+1):
        ret = ret*if_then_else(i<=n, i, 1)
        
    return ret

def factorial_while(n):
    ret = 1
    busy = 1
    
    for i in range(2, FAC_MAX+1):
        busy = busy&(i!=n+1)
        ret = ret*if_then_else(busy, i, 1)
    
    return ret

def factorial_while_2(n):
    _=BranchingValues()
    _.ret=1
    for i in _range(2,n+1,max=FAC_MAX+1):
        _.ret=_.ret*i
    _endfor()
    return _.ret

def benchmark_factorial(nm, fn):
    numc = 0
    def callback(num):
        nonlocal numc
        numc = num
        
    ret = benchmark(callback)(fn)(PrivVal(FAC_TEST))
    ret2 = fn(PrivVal(FAC_MAX))
    print("%-30s: output=%d, %d, constraints=%d" % (nm, ret.value, ret2.value, numc))

benchmark_factorial("factorial_if_comparison", factorial_if_comparison)
benchmark_factorial("factorial_while", factorial_while)
benchmark_factorial("factorial_while_2", factorial_while_2)
