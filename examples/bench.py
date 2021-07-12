# Copyright (C) Meilof Veeningen

import pysnark.nobackend
import pysnark.runtime

from pysnark.runtime import PrivVal, LinComb, benchmark, guarded
from pysnark.boolean import LinCombBool
from pysnark.branching import if_then_else, _while

def count_ops(fn):
    numc = 0
    def callback(num):
        nonlocal numc
        numc = num
    
    benchmark(callback)(fn)()
    
    return numc

def benchmark_con_bl(fn):
    # unguarded
    pysnark.runtime.bitlength = 3
    op1 = count_ops(fn)
    pysnark.runtime.bitlength = 5
    op2 = count_ops(fn)
    if op1!=op2:
        raise AssertionError("benchmark_const_nl: function not independent from bitlength")
        
    pysnark.runtime.bitlength = 3
    op3 = count_ops(guarded(LinComb.ONE)(fn))
    pysnark.runtime.bitlength = 5
    op4 = count_ops(guarded(LinComb.ONE)(fn))
    if op3!=op4:
        raise AssertionError("benchmark_const_nl: function not independent from bitlength")
        
    return str(op1) + " [" + str(op3) + "]"

def benchmark_lin_bl(fn):
    pysnark.runtime.bitlength = 3
    op1 = count_ops(fn)
    pysnark.runtime.bitlength = 5
    op2 = count_ops(fn)
    pysnark.runtime.bitlength = 7
    op3 = count_ops(fn)
    coef = (op2-op1)//2
    const = op1-3*coef
    if op3!=const+7*coef:
        raise AssertionError("benchmark_lin_bl: constraints not linear in bitlength")
        
    pysnark.runtime.bitlength = 3
    op4 = count_ops(guarded(LinComb.ONE)(fn))
    pysnark.runtime.bitlength = 5
    op5 = count_ops(guarded(LinComb.ONE)(fn))
    pysnark.runtime.bitlength = 7
    op6 = count_ops(guarded(LinComb.ONE)(fn))
    coef2 = (op5-op4)//2
    const2 = op4-3*coef2
    if op6!=const2+7*coef2:
        raise AssertionError("benchmark_lin_bl: constraints not linear in bitlength")

    return str(coef)+"*k+"+str(const) + " [" + str(coef2)+"*k+"+str(const2) + "]"

def several(lst):
    if len(set(lst))!=1:
        raise AssertionError("Different values in benchmerk")
    return lst[0]

print("<, <=, >, >=              ", several([benchmark_lin_bl(lambda:LinComb.ZERO<LinComb.ZERO),
                                       benchmark_lin_bl(lambda:LinComb.ZERO<=LinComb.ZERO),
                                       benchmark_lin_bl(lambda:LinComb.ZERO>LinComb.ZERO),
                                       benchmark_lin_bl(lambda:LinComb.ZERO>=LinComb.ZERO)]))
print("assert_lt, _le, _gt, _ge  ", several([benchmark_lin_bl(lambda:LinComb.ZERO.assert_lt(1)),
                                             benchmark_lin_bl(lambda:LinComb.ZERO.assert_le(1)),
                                             benchmark_lin_bl(lambda:LinComb.ONE.assert_gt(0)),
                                             benchmark_lin_bl(lambda:LinComb.ZERO.assert_ge(0))]))

print("__eq__              ", benchmark_con_bl(lambda:LinComb.ZERO==LinComb.ZERO))
print("assert_eq           ", benchmark_con_bl(lambda:LinComb.ZERO.assert_eq(LinComb.ZERO)))

print("__ne__              ", benchmark_con_bl(lambda:LinComb.ZERO!=LinComb.ZERO))
print("assert_ne           ", benchmark_con_bl(lambda:LinComb.ZERO.assert_ne(LinComb.ONE)))

print("__add__ (base)      ", benchmark_con_bl(lambda:LinComb.ZERO+0))
print("__add__ (lc)        ", benchmark_con_bl(lambda:LinComb.ZERO+LinComb.ZERO))

print("__sub__ (base)      ", benchmark_con_bl(lambda:LinComb.ZERO-0))
print("__sub__ (lc)        ", benchmark_con_bl(lambda:LinComb.ZERO-LinComb.ZERO))

print("__mul__ (const)     ", benchmark_con_bl(lambda:LinComb.ZERO*0))
print("__mul__ (val)       ", benchmark_con_bl(lambda:LinComb.ZERO*LinComb.ZERO))

print("__truediv__ (const) ", benchmark_con_bl(lambda:LinComb.ONE/1))
print("__truediv__ (val)   ", benchmark_con_bl(lambda:LinComb.ONE/LinComb.ONE))

print("LimCombBool (val)   ", benchmark_con_bl(lambda:LinCombBool(LinComb.ONE)))