import pytest
from pysnark import runtime
from pysnark import fixedpoint
from pysnark.runtime import PrivVal
from pysnark.fixedpoint import PrivValFxp, PubValFxp

class TestLinCombFxp():
    def test_fixed_point(self):
        assert PrivValFxp(1).lc.value == 1 << fixedpoint.resolution
        assert PrivValFxp(1.0).lc.value == 1 << fixedpoint.resolution

    def test_priv_val(self):
        assert PrivValFxp(3).val() == 3
        assert PrivValFxp(3.125).val() == 3.125

    def test_pub_val(self):
        assert PubValFxp(3).val() == 3
        assert PubValFxp(3.125).val() == 3.125

    def test_resolution(self):
        fixedpoint.resolution = 4

        PubValFxp(3.0625)
        with pytest.warns(UserWarning):
            PubValFxp(3.06255)

        fixedpoint.resolution = 8

        with pytest.warns(UserWarning):
            PubValFxp(3.14)

    def test_add(self):
        assert (PrivValFxp(1.0) + 2).val() == 3.0
        assert (PrivValFxp(1.0) + 2.0).val() == 3.0
        assert (2 + PrivValFxp(1.0)).val() == 3.0
        assert (2.0 + PrivValFxp(1.0)).val() == 3.0
        assert (PrivValFxp(1.0) + PrivValFxp(2.0)).val() == 3.0
        assert (PrivValFxp(1.0) + PrivVal(2)).val() == 3.0
        assert (PrivVal(2) + PrivValFxp(1.0)).val() == 3.0

    def test_mul(self):
        assert (PrivValFxp(2.0) * 2).val() == 4
        assert (PrivValFxp(2.0) * 2.0).val() == 4
        assert (2 * PrivValFxp(2.0)).val() == 4
        assert (2.0 * PrivValFxp(2.0)).val() == 4
        assert (PrivValFxp(2.0) * PrivValFxp(2.0)).val() == 4
        assert (PrivValFxp(2.0) * PrivVal(2)).val() == 4
        assert (PrivVal(2) * PrivValFxp(2.0)).val() == 4

    def test_sub(self):
        assert (PrivValFxp(2.0) - 1).val() == 1.0
        assert (PrivValFxp(2.0) - 1.0).val() == 1.0
        assert (2 - PrivValFxp(1.0)).val() == 1.0
        assert (2.0 - PrivValFxp(1.0)).val() == 1.0
        assert (PrivValFxp(2.0) - PrivValFxp(1.0)).val() == 1.0
        assert (PrivValFxp(2.0) - PrivVal(1)).val() == 1.0
        assert (PrivVal(2) - PrivValFxp(1.0)).val() == 1.0

    def test_div_integer(self):
        assert (PrivValFxp(4.0) / 2).val() == 2.0
        assert (PrivValFxp(4.0) / 2.0).val() == 2.0
        assert (4 / PrivValFxp(2.0)).val() == 2.0
        assert (4.0 / PrivValFxp(2.0)).val() == 2.0
        assert (PrivValFxp(4.0) / PrivValFxp(2.0)).val() == 2.0
        assert (PrivValFxp(4.0) / PrivVal(2)).val() == 2.0
        assert (PrivVal(4) / PrivValFxp(2.0)).val() == 2.0

    def test_div_fraction(self):
        assert (PrivValFxp(5.0) / 2).val() == 2.5
        assert (PrivValFxp(5.0) / 2.0).val() == 2.5
        assert (5 / PrivValFxp(2.0)).val() == 2.5
        assert (5.0 / PrivValFxp(2.0)).val() == 2.5
        assert (PrivValFxp(5.0) / PrivValFxp(2.0)).val() == 2.5
        assert (PrivValFxp(5.0) / PrivVal(2)).val() == 2.5
        assert (PrivVal(5) / PrivValFxp(2.0)).val() == 2.5

    def test_floor_div(self):
        assert (PrivValFxp(5.0) // 2).val() == 2.0
        assert (PrivValFxp(5.0) // 2.0).val() == 2.0
        assert (5 // PrivValFxp(2.0)).val() == 2.0
        assert (5.0 // PrivValFxp(2.0)).val() == 2.0
        assert (PrivValFxp(5.0) // PrivValFxp(2.0)).val() == 2.0
        assert (PrivValFxp(5.0) // PrivVal(2)).val() == 2.0
        assert (PrivVal(5) // PrivValFxp(2.0)).val() == 2.0

    def test_mod(self):
        assert (PrivValFxp(5) % 2).val() == 1.0
        assert (PrivValFxp(5) % 2.0).val() == 1.0
        assert (5 % PrivValFxp(2)).val() == 1.0
        assert (5.0 % PrivValFxp(2)).val() == 1.0
        assert (PrivValFxp(5) % PrivValFxp(2)).val() == 1.0
        assert (PrivValFxp(5) % PrivVal(2)).val() == 1.0
        assert (PrivVal(5) % PrivValFxp(2)).val() == 1.0

        assert (PrivValFxp(5) % 1).val() == 0.0
        assert (PrivValFxp(5) % 1.0).val() == 0.0
        assert (5 % PrivValFxp(1)).val() == 0.0
        assert (5.0 % PrivValFxp(1)).val() == 0.0
        assert (PrivValFxp(5) % PrivValFxp(1)).val() == 0.0
        assert (PrivValFxp(5) % PrivVal(1)).val() == 0.0
        assert (PrivVal(5) % PrivValFxp(1)).val() == 0.0

    def test_pow(self):
        assert (PrivValFxp(2) ** 2).val() == 4.0
        # assert (PrivValFxp(2) ** 2.0).val() == 4.0
        # assert (2 ** PrivValFxp(2)).val() == 4.0
        # assert (2.0 ** PrivValFxp(2)).val() == 4.0
        # assert (PrivValFxp(2) ** PrivValFxp(2)).val() == 4.0
        # assert (PrivValFxp(2) ** PrivVal(2)).val() == 4.0
        # assert (PrivVal(2) ** PrivValFxp(2)).val() == 4.0

        assert (PrivValFxp(2) ** 0).val() == 1.0
        # assert (PrivValFxp(2) ** 0.0).val() == 1.0
        # assert (2 ** PrivValFxp(0)).val() == 1.0
        # assert (2.0 ** PrivValFxp(0)).val() == 1.0
        # assert (PrivValFxp(2) ** PrivValFxp(0)).val() == 1.0
        # assert (PrivValFxp(2) ** PrivVal(0)).val() == 1.0
        # assert (PrivVal(2) ** PrivValFxp(0)).val() == 1.0

    def test_rshift(self):
        pass
        # assert (PrivValFxp(2.0) << 2).val() == 8.0
        # assert (PrivValFxp(2.0) << 2.0).val() == 8.0
        # assert (2 << PrivValFxp(2.0)).val() == 8.0
        # assert (2.0 << PrivValFxp(2.0)).val() == 8.0
        # assert (PrivValFxp(2.0) << PrivValFxp(2.0)).val() == 8.0
        # assert (PrivValFxp(2.0) << PrivVal(2)).val() == 8.0
        # assert (PrivVal(2) << PrivValFxp(2.0)).val() == 8.0

    def test_lshift(self):
        pass
        # assert (PrivValFxp(8.0) >> 2).val() == 2.0
        # assert (PrivValFxp(8.0) >> 2.0).val() == 2.0
        # assert (8 >> PrivValFxp(2.0)).val() == 2.0
        # assert (8.0 >> PrivValFxp(2.0)).val() == 2.0
        # assert (PrivValFxp(8.0) >> PrivValFxp(2.0)).val() == 2.0
        # assert (PrivValFxp(8.0) >> PrivVal(2)).val() == 2.0
        # assert (PrivVal(8.0) >> PrivValFxp(2.0)).val() == 2.0