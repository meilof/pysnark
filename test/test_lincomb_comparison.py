import pytest
from pysnark.runtime import PrivVal
from pysnark.boolean import LinCombBool

class TestLinCombComparison():
    def test_eq(self):
        assert (3 == PrivVal(3)).val() == 1
        assert (PrivVal(3) == 3).val() == 1
        assert (PrivVal(3) == PrivVal(3)).val() == 1
        assert isinstance(PrivVal(3) == 3, LinCombBool)

        assert (2 == PrivVal(3)).val() == 0
        assert (PrivVal(3) == 2).val() == 0
        assert (PrivVal(3) == PrivVal(2)).val() == 0
        assert (PrivVal(2) == PrivVal(3)).val() == 0
        assert isinstance(PrivVal(3) == 2, LinCombBool)

    def test_assert_eq(self):
        PrivVal(3).assert_eq(3)
        PrivVal(3).assert_eq(PrivVal(3))

        with pytest.raises(AssertionError):
            PrivVal(3).assert_eq(2)
        with pytest.raises(AssertionError):
            PrivVal(3).assert_eq(PrivVal(2))
        with pytest.raises(AssertionError):
            PrivVal(2).assert_eq(PrivVal(3))

    def test_ne(self):
        assert (3 != PrivVal(2)).val() == 1
        assert (PrivVal(3) != 2).val() == 1
        assert (PrivVal(3) != PrivVal(2)).val() == 1
        assert (PrivVal(2) != PrivVal(3)).val() == 1
        assert isinstance(PrivVal(3) != 2, LinCombBool)

        assert (3 != PrivVal(3)).val() == 0
        assert (PrivVal(3) != 3).val() == 0
        assert (PrivVal(3) != PrivVal(3)).val() == 0
        assert isinstance(PrivVal(3) != 3, LinCombBool)

    def test_assert_ne(self):
        PrivVal(3).assert_ne(2)
        PrivVal(3).assert_ne(PrivVal(2))
        PrivVal(2).assert_ne(PrivVal(3))

        with pytest.raises(AssertionError):
            PrivVal(3).assert_ne(3)
        with pytest.raises(AssertionError):
            PrivVal(3).assert_ne(PrivVal(3))

    def test_lt(self):
        assert (3 < PrivVal(5)).val() == 1
        assert (PrivVal(3) < 5).val() == 1
        assert (PrivVal(3) < PrivVal(5)).val() == 1
        assert isinstance(PrivVal(3) < 5, LinCombBool)

        assert (3 < PrivVal(1)).val() == 0
        assert (PrivVal(3) < 1).val() == 0
        assert (PrivVal(3) < PrivVal(1)).val() == 0
        assert isinstance(PrivVal(3) < 1, LinCombBool)

    def test_assert_lt(self):
        PrivVal(3).assert_lt(5)
        PrivVal(3).assert_lt(PrivVal(5))

        with pytest.raises(AssertionError):
            PrivVal(3).assert_lt(1)
        with pytest.raises(AssertionError):
            PrivVal(3).assert_lt(PrivVal(1))
        with pytest.raises(AssertionError):
            PrivVal(3).assert_lt(3)
        with pytest.raises(AssertionError):
            PrivVal(3).assert_lt(PrivVal(3))

    def test_le(self):
        assert (3 <= PrivVal(3)).val() == 1
        assert (3 <= PrivVal(5)).val() == 1
        assert (PrivVal(3) <= 3).val() == 1
        assert (PrivVal(3) <= 5).val() == 1
        assert (PrivVal(3) <= PrivVal(3)).val() == 1
        assert (PrivVal(3) <= PrivVal(5)).val() == 1
        assert isinstance(PrivVal(3) <= 5, LinCombBool)

        assert (3 <= PrivVal(1)).val() == 0
        assert (PrivVal(3) <= 1).val() == 0
        assert (PrivVal(3) <= PrivVal(1)).val() == 0
        assert isinstance(PrivVal(3) <= 1, LinCombBool)

    def test_assert_le(self):
        PrivVal(3).assert_le(3)
        PrivVal(3).assert_le(5)
        PrivVal(3).assert_le(PrivVal(3))
        PrivVal(3).assert_le(PrivVal(5))

        with pytest.raises(AssertionError):
            PrivVal(3).assert_le(1)
        with pytest.raises(AssertionError):
            PrivVal(3).assert_le(PrivVal(1))

    def test_gt(self):
        assert (5 > PrivVal(3)).val() == 1
        assert (PrivVal(5) > 3).val() == 1
        assert (PrivVal(5) > PrivVal(3)).val() == 1
        assert isinstance(PrivVal(5) > 3, LinCombBool)

        assert (1 > PrivVal(3)).val() == 0
        assert (PrivVal(1) > 3).val() == 0
        assert (PrivVal(1) > PrivVal(3)).val() == 0
        assert isinstance(PrivVal(1) > 3, LinCombBool)

    def test_assert_gt(self):
        PrivVal(5).assert_gt(3)
        PrivVal(5).assert_gt(PrivVal(3))

        with pytest.raises(AssertionError):
            PrivVal(1).assert_gt(1)
        with pytest.raises(AssertionError):
            PrivVal(1).assert_gt(PrivVal(1))
        with pytest.raises(AssertionError):
            PrivVal(1).assert_gt(3)
        with pytest.raises(AssertionError):
            PrivVal(1).assert_gt(PrivVal(3))

    def test_ge(self):
        assert (5 >= PrivVal(3)).val() == 1
        assert (5 >= PrivVal(3)).val() == 1
        assert (PrivVal(5) >= 3).val() == 1
        assert (PrivVal(5) >= 3).val() == 1
        assert (PrivVal(5) >= PrivVal(3)).val() == 1
        assert (PrivVal(5) >= PrivVal(3)).val() == 1
        assert isinstance(PrivVal(5) >= 3, LinCombBool)

        assert (1 >= PrivVal(3)).val() == 0
        assert (PrivVal(1) >= 3).val() == 0
        assert (PrivVal(1) >= PrivVal(3)).val() == 0
        assert isinstance(PrivVal(1) >= 3, LinCombBool)

    def test_assert_ge(self):
        PrivVal(3).assert_ge(3)
        PrivVal(5).assert_ge(3)
        PrivVal(3).assert_ge(PrivVal(3))
        PrivVal(5).assert_ge(PrivVal(3))

        with pytest.raises(AssertionError):
            PrivVal(1).assert_ge(3)
        with pytest.raises(AssertionError):
            PrivVal(1).assert_ge(PrivVal(3))

    def test_assert_range(self):
        PrivVal(1).assert_range(PrivVal(1), PrivVal(2))
        with pytest.raises(AssertionError):
            PrivVal(0).assert_range(PrivVal(1), PrivVal(2))
        with pytest.raises(AssertionError):
            PrivVal(2).assert_range(PrivVal(1), PrivVal(2))

    def test_check_zero(self):
        assert PrivVal(0).check_zero().val() == 1
        assert PrivVal(1).check_zero().val() == 0

    def test_check_nonzero(self):
        assert PrivVal(0).check_nonzero().val() == 0
        assert PrivVal(1).check_nonzero().val() == 1
        