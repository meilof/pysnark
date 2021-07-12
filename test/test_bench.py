# Copyright (C) Meilof Veeningen

import pysnark.runtime

from pysnark.runtime import LinComb, PrivVal, benchmark
from pysnark.fixedpoint import PrivValFxp, LinCombFxp
from pysnark.boolean import LinCombBool

BITLENGTH_1 = 10
BITLENGTH_2 = 12
BITLENGTH_3 = 14

def count_ops(fn):
    numc = 0
    def callback(num):
        nonlocal numc
        numc = num
    
    benchmark(callback)(fn)()
    return numc

def assert_constant_constraints(fn):
    pysnark.runtime.bitlength = BITLENGTH_1
    op1 = count_ops(fn)
    pysnark.runtime.bitlength = BITLENGTH_2
    op2 = count_ops(fn)

    if op1 != op2:
        raise AssertionError("Constraints not independent from bitlength")
    
    return op1

def assert_linear_constraints(fn):
    pysnark.runtime.bitlength = BITLENGTH_1
    op1 = count_ops(fn)
    pysnark.runtime.bitlength = BITLENGTH_2
    op2 = count_ops(fn)
    pysnark.runtime.bitlength = BITLENGTH_3
    op3 = count_ops(fn)
    
    coef = (op2 - op1) // (BITLENGTH_2 - BITLENGTH_1)
    const = op1 - BITLENGTH_1 * coef

    if op3 != const + BITLENGTH_3 * coef:
        raise AssertionError("Constraints not linear in bitlength")
    
    return (coef,const)

class TestBench():

    def test_lincomb_arithmetic(self):
        assert assert_constant_constraints(lambda: PrivVal(0) + 0) == 0
        assert assert_constant_constraints(lambda: PrivVal(0) - 0) == 0
        assert assert_constant_constraints(lambda: PrivVal(0) * 0) == 0
        assert assert_constant_constraints(lambda: PrivVal(1) / 1) == 0
        assert assert_linear_constraints(lambda: PrivVal(1) // 1) == (2,4)
        assert assert_linear_constraints(lambda: PrivVal(1) % 1) == (2,4)
        assert assert_constant_constraints(lambda: PrivVal(1) ** 5) == 4

        assert assert_constant_constraints(lambda: PrivVal(0) + PrivVal(0)) == 0
        assert assert_constant_constraints(lambda: PrivVal(0) - PrivVal(0)) == 0
        assert assert_constant_constraints(lambda: PrivVal(0) * PrivVal(0)) == 1
        assert assert_constant_constraints(lambda: PrivVal(1) / PrivVal(1)) == 1
        assert assert_linear_constraints(lambda: PrivVal(1) // PrivVal(1)) == (2,4)
        assert assert_linear_constraints(lambda: PrivVal(1) % PrivVal(1)) == (2,4)
        assert assert_linear_constraints(lambda: PrivVal(1) ** PrivVal(0)) == (7,1)
        assert assert_linear_constraints(lambda: PrivVal(1) ** PrivVal(1)) == (7,1)

    def test_lincomb_comparison(self):
        assert assert_constant_constraints(lambda: PrivVal(0) == 0) == 2
        assert assert_constant_constraints(lambda: PrivVal(0) != 0) == 2

        assert assert_constant_constraints(lambda: PrivVal(0) == PrivVal(0)) == 2
        assert assert_constant_constraints(lambda: PrivVal(0) != PrivVal(1)) == 2

        assert assert_linear_constraints(lambda: PrivVal(0) < PrivVal(0)) == (1,2)
        assert assert_linear_constraints(lambda: PrivVal(0) <= PrivVal(0)) == (1,2)
        
        assert assert_linear_constraints(lambda: PrivVal(0) > PrivVal(0)) == (1,2)
        assert assert_linear_constraints(lambda: PrivVal(0) >= PrivVal(0)) == (1,2)

    def test_lincomb_check(self):
        assert assert_constant_constraints(lambda: PrivVal(1).check_zero()) == 2
        assert assert_constant_constraints(lambda: PrivVal(1).check_nonzero()) == 2
        assert assert_linear_constraints(lambda: PrivVal(1).check_positive()) == (1,2)

    def test_lincomb_assertion(self):
        assert assert_constant_constraints(lambda: PrivVal(0).assert_zero()) == 1
        assert assert_constant_constraints(lambda: PrivVal(1).assert_nonzero()) == 1

        assert assert_linear_constraints(lambda: PrivVal(1).assert_positive()) == (1,1)
        assert assert_linear_constraints(lambda: PrivVal(1).assert_range(PrivVal(0), PrivVal(2))) == (2, 2)

        assert assert_constant_constraints(lambda: PrivVal(0).assert_eq(PrivVal(0))) == 1
        assert assert_constant_constraints(lambda: PrivVal(0).assert_ne(PrivVal(1))) == 1

        assert assert_linear_constraints(lambda: PrivVal(0).assert_lt(PrivVal(1))) == (1,1)
        assert assert_linear_constraints(lambda: PrivVal(0).assert_le(PrivVal(1))) == (1,1)

        assert assert_linear_constraints(lambda: PrivVal(1).assert_gt(PrivVal(0))) == (1,1)
        assert assert_linear_constraints(lambda: PrivVal(0).assert_ge(PrivVal(0))) == (1,1)

    def test_lincomb_bitwise(self):
        assert assert_linear_constraints(lambda: PrivVal(0).to_bits()) == (1,1)
        assert assert_constant_constraints(lambda: LinComb.from_bits([PrivVal(1), PrivVal(0), PrivVal(1)])) == 0

        assert assert_constant_constraints(lambda: PrivVal(1) << 1) == 0
        assert assert_constant_constraints(lambda: PrivVal(1) << 2) == 0
        assert assert_linear_constraints(lambda: PrivVal(1) >> 1) == (1,1)
        assert assert_linear_constraints(lambda: PrivVal(1) >> 2) == (1,1)
        assert assert_linear_constraints(lambda: PrivVal(1) << PrivVal(1)) == (7,2)
        assert assert_linear_constraints(lambda: PrivVal(1) >> PrivVal(1)) == (9,5)

        assert assert_constant_constraints(lambda: PrivVal(0) & 1) == 0
        assert assert_constant_constraints(lambda: PrivVal(0) | 1) == 0
        assert assert_constant_constraints(lambda: PrivVal(0) ^ 1) == 0

        assert assert_linear_constraints(lambda: PrivVal(0) & PrivVal(1)) == (3,2)
        assert assert_linear_constraints(lambda: PrivVal(0) | PrivVal(1)) == (3,2)
        assert assert_linear_constraints(lambda: PrivVal(0) ^ PrivVal(1)) == (3,2)

    def test_lincombfxp_arithmetic(self):
        assert assert_constant_constraints(lambda: LinCombFxp(PrivVal(1))) == 0

        assert assert_constant_constraints(lambda: PrivValFxp(0) + 0) == 0
        assert assert_constant_constraints(lambda: PrivValFxp(0) - 0) == 0
        assert assert_constant_constraints(lambda: PrivValFxp(0) * 0) == 0
        assert assert_linear_constraints(lambda: PrivValFxp(1) / 1) == (2,4)
        assert assert_linear_constraints(lambda: PrivValFxp(1) // 1) == (2,4)
        assert assert_linear_constraints(lambda: PrivValFxp(1) % 1) == (2,4)
        assert assert_constant_constraints(lambda: PrivValFxp(1) ** 5) == 4

        assert assert_constant_constraints(lambda: PrivValFxp(0) + PrivVal(0)) == 0
        assert assert_constant_constraints(lambda: PrivValFxp(0) - PrivVal(0)) == 0
        assert assert_constant_constraints(lambda: PrivValFxp(0) * PrivVal(0)) == 1
        assert assert_linear_constraints(lambda: PrivValFxp(1) / PrivVal(1)) == (2,4)
        assert assert_linear_constraints(lambda: PrivValFxp(1) // PrivVal(1)) == (2,4)
        assert assert_linear_constraints(lambda: PrivValFxp(1) % PrivVal(1)) == (2,4)
        # assert assert_linear_constraints(lambda: PrivValFxp(1) ** PrivVal(0)) == 41
        # assert assert_linear_constraints(lambda: PrivValFxp(1) ** PrivVal(1)) == 41

        assert assert_constant_constraints(lambda: PrivValFxp(0) + PrivValFxp(0)) == 0
        assert assert_constant_constraints(lambda: PrivValFxp(0) - PrivValFxp(0)) == 0
        assert assert_constant_constraints(lambda: PrivValFxp(0) * PrivValFxp(0)) == 1
        assert assert_linear_constraints(lambda: PrivValFxp(1) / PrivValFxp(1)) == (2,4)
        assert assert_linear_constraints(lambda: PrivValFxp(1) // PrivValFxp(1)) == (2,4)
        assert assert_linear_constraints(lambda: PrivValFxp(1) % PrivValFxp(1)) == (2,4)
        # assert assert_linear_constraints(lambda: PrivValFxp(1) ** PrivValFxp(0)) == 41
        # assert assert_linear_constraints(lambda: PrivValFxp(1) ** PrivValFxp(1)) == 41

    def test_lincombfxp_comparison(self):
        assert assert_constant_constraints(lambda: PrivValFxp(0) == 0) == 2
        assert assert_constant_constraints(lambda: PrivValFxp(0) != 0) == 2

        assert assert_constant_constraints(lambda: PrivValFxp(0) == PrivVal(0)) == 2
        assert assert_constant_constraints(lambda: PrivValFxp(0) != PrivVal(1)) == 2

        assert assert_linear_constraints(lambda: PrivValFxp(0) < PrivVal(0)) == (1,2)
        assert assert_linear_constraints(lambda: PrivValFxp(0) <= PrivVal(0)) == (1,2)
        
        assert assert_linear_constraints(lambda: PrivValFxp(0) > PrivVal(0)) == (1,2)
        assert assert_linear_constraints(lambda: PrivValFxp(0) >= PrivVal(0)) == (1,2)

    def test_lincombfxp_check(self):
        assert assert_constant_constraints(lambda: PrivValFxp(1).check_zero()) == 2
        assert assert_constant_constraints(lambda: PrivValFxp(1).check_nonzero()) == 2
        assert assert_linear_constraints(lambda: PrivValFxp(1).check_positive()) == (1,2)

    def test_lincombfxp_assertion(self):
        assert assert_constant_constraints(lambda: PrivValFxp(0).assert_zero()) == 1
        assert assert_constant_constraints(lambda: PrivValFxp(1).assert_nonzero()) == 1

        assert assert_linear_constraints(lambda: PrivValFxp(1).assert_positive()) == (1,1)
        assert assert_linear_constraints(lambda: PrivValFxp(1).assert_range(PrivVal(0), PrivVal(2))) == (2, 2)

        assert assert_constant_constraints(lambda: PrivValFxp(0).assert_eq(PrivVal(0))) == 1
        assert assert_constant_constraints(lambda: PrivValFxp(0).assert_ne(PrivVal(1))) == 1

        assert assert_linear_constraints(lambda: PrivValFxp(0).assert_lt(PrivVal(1))) == (1,1)
        assert assert_linear_constraints(lambda: PrivValFxp(0).assert_le(PrivVal(1))) == (1,1)

        assert assert_linear_constraints(lambda: PrivValFxp(1).assert_gt(PrivVal(0))) == (1,1)
        assert assert_linear_constraints(lambda: PrivValFxp(0).assert_ge(PrivVal(0))) == (1,1)

    def test_lincombbool(self):
        # Construct LinCombBool outside lambda, since construction costs 1 constraint
        val = LinCombBool(PrivVal(1))

        assert assert_constant_constraints(lambda: LinCombBool(PrivVal(1))) == 1
        assert assert_constant_constraints(lambda: -val) == 0

        assert assert_constant_constraints(lambda: ~val) == 0
        assert assert_constant_constraints(lambda: val & val) == 1
        assert assert_constant_constraints(lambda: val | val) == 1
        assert assert_constant_constraints(lambda: val ^ val) == 1

        assert assert_constant_constraints(lambda: val + PrivVal(2)) == 0
        assert assert_constant_constraints(lambda: val - PrivVal(2)) == 0
        assert assert_constant_constraints(lambda: val * PrivVal(2)) == 1
        assert assert_constant_constraints(lambda: val ** PrivVal(2)) == 2