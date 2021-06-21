from pysnark import runtime
from pysnark.runtime import PrivVal, PubVal

class TestLinComb():
    def test_priv_val(self):
        assert PrivVal(3).val() == 3

    def test_pub_val(self):
        assert PubVal(3).val() == 3

    def test_add(self):
        assert (PubVal(1) + 2).val() == 3
        assert (2 + PubVal(1)).val() == 3
        assert (PrivVal(1) + PrivVal(2)).val() == 3

    def test_mul(self):
        assert (PrivVal(2) * 2).val() == 4
        assert (2 * PrivVal(2)).val() == 4
        assert (PrivVal(2) * PrivVal(2)).val() == 4

    def test_sub(self):
        assert (PrivVal(2) - 1).val() == 1
        assert (2 - PrivVal(1)).val() == 1
        assert (PrivVal(2) - PrivVal(1)).val() == 1

    def test_div_integer(self):
        assert (PrivVal(4) / 2).val() == 2
        assert (4 / PrivVal(2)).val() == 2
        assert (PrivVal(4) / PrivVal(2)).val() == 2

    def test_floor_div(self):
        assert (PrivVal(4) // 2).val() == 2
        assert (4 // PrivVal(2)).val() == 2
        assert (PrivVal(4) // PrivVal(2)).val() == 2

        assert (PrivVal(5) // 2).val() == 2
        assert (5 // PrivVal(2)).val() == 2
        assert (PrivVal(5) // PrivVal(2)).val() == 2

    def test_mod(self):
        assert (PrivVal(5) % 2).val() == 1
        assert (5 % PrivVal(2)).val() == 1
        assert (PrivVal(5) % PrivVal(2)).val() == 1

        assert (PrivVal(5) % 1).val() == 0
        assert (5 % PrivVal(1)).val() == 0
        assert (PrivVal(5) % PrivVal(1)).val() == 0

    def test_pow(self):
        runtime.bitlength = 5

        assert (PrivVal(2) ** 4).val() == 16
        assert (2 ** PrivVal(4)).val() == 16
        assert (PrivVal(2) ** PrivVal(4)).val() == 16

        assert (PrivVal(2) ** 0).val() == 1
        assert (2 ** PrivVal(0)).val() == 1
        assert (PrivVal(2) ** PrivVal(0)).val() == 1

        runtime.bitlength = 16

    def test_rshift(self):
        runtime.bitlength = 5

        assert (PrivVal(2) << 2).val() == 8
        assert (2 << PrivVal(2)).val() == 8
        assert (PrivVal(2) << PrivVal(2)).val() == 8

        runtime.bitlength = 16

    def test_lshift(self):
        runtime.bitlength = 5

        assert (PrivVal(8) >> 2).val() == 2
        assert (8 >> PrivVal(2)).val() == 2
        assert (PrivVal(8) >> PrivVal(2)).val() == 2

        runtime.bitlength = 16

    def test_lt(self):
        assert((PrivVal(1) < 2).val() == 1)
        assert((1 < PrivVal(2)).val() == 1)
        assert((PrivVal(1) < PrivVal(2)).val() == 1)

        assert((PrivVal(2) < 1).val() == 0)
        assert((2 < PrivVal(1)).val() == 0)
        assert((PrivVal(2) < PrivVal(1)).val() == 0)

        assert((PrivVal(1) < 1).val() == 0)
        assert((1 < PrivVal(1)).val() == 0)
        assert((PrivVal(1) < PrivVal(1)).val() == 0)

    def test_gt(self):
        assert((PrivVal(2) > 1).val() == 1)
        assert((2 > PrivVal(1)).val() == 1)
        assert((PrivVal(2) > PrivVal(1)).val() == 1)

        assert((PrivVal(1) > 2).val() == 0)
        assert((1 > PrivVal(2)).val() == 0)
        assert((PrivVal(1) > PrivVal(2)).val() == 0)

        assert((PrivVal(1) > 1).val() == 0)
        assert((1 > PrivVal(1)).val() == 0)
        assert((PrivVal(1) > PrivVal(1)).val() == 0)

    def test_lte(self):
        assert((PrivVal(1) <= 2).val() == 1)
        assert((1 <= PrivVal(2)).val() == 1)
        assert((PrivVal(1) <= PrivVal(2)).val() == 1)

        assert((PrivVal(2) <= 1).val() == 0)
        assert((2 <= PrivVal(1)).val() == 0)
        assert((PrivVal(2) <= PrivVal(1)).val() == 0)

        assert((PrivVal(1) <= 1).val() == 1)
        assert((1 <= PrivVal(1)).val() == 1)
        assert((PrivVal(1) <= PrivVal(1)).val() == 1)

    def test_gte(self):
        assert((PrivVal(2) >= 1).val() == 1)
        assert((2 >= PrivVal(1)).val() == 1)
        assert((PrivVal(2) >= PrivVal(1)).val() == 1)

        assert((PrivVal(1) >= 2).val() == 0)
        assert((1 >= PrivVal(2)).val() == 0)
        assert((PrivVal(1) >= PrivVal(2)).val() == 0)

        assert((PrivVal(1) >= 1).val() == 1)
        assert((1 >= PrivVal(1)).val() == 1)
        assert((PrivVal(1) >= PrivVal(1)).val() == 1)

    def test_eq(self):
        assert((PrivVal(2) == 2).val() == 1)
        assert((2 == PrivVal(2)).val() == 1)
        assert((PrivVal(2) == PrivVal(2)).val() == 1)

        assert((PrivVal(2) == 1).val() == 0)
        assert((2 == PrivVal(1)).val() == 0)
        assert((PrivVal(2) == PrivVal(1)).val() == 0)

    def test_neq(self):
        assert((PrivVal(2) != 1).val() == 1)
        assert((2 != PrivVal(1)).val() == 1)
        assert((PrivVal(2) != PrivVal(1)).val() == 1)

        assert((PrivVal(2) != 2).val() == 0)
        assert((2 != PrivVal(2)).val() == 0)
        assert((PrivVal(2) != PrivVal(2)).val() == 0)
