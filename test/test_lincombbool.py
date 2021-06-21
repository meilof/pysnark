import pytest
from pysnark.runtime import PrivVal
from pysnark.boolean import PrivValBool, PubValBool

class TestLinCombBool():
    def test_bool(self):
        PubValBool(0)
        PubValBool(1)
        with pytest.raises(ValueError):
            PubValBool(2)
        with pytest.raises(RuntimeError):
            PubValBool(2.5)

    def test_priv_val(self):
        assert PrivValBool(0).val() == 0
        assert PrivValBool(1).val() == 1

    def test_pub_val(self):
        assert PubValBool(0).val() == 0
        assert PubValBool(1).val() == 1

    def test_add(self):
        assert (PrivValBool(1) + PrivValBool(1)).val() == 2
        assert (PrivVal(1) + PrivValBool(1)).val() == 2
        assert (PrivValBool(1) + PrivVal(1)).val() == 2
        assert (1 + PrivValBool(1)).val() == 2
        assert (PrivValBool(1) + 1).val() == 2

    def test_mul(self):
        assert (PrivValBool(1) * PrivValBool(0)).val() == 0
        assert (PrivVal(2) * PrivValBool(0)).val() == 0
        assert (PrivValBool(0) * PrivVal(2)).val() == 0

        assert (PrivVal(2) * PrivValBool(1)).val() == 2
        assert (PrivValBool(1) * PrivVal(2)).val() == 2
        assert (2 * PrivValBool(1)).val() == 2
        assert (PrivValBool(1) * 2).val() == 2

    def test_sub(self):
        assert (PrivValBool(1) - PrivValBool(1)).val() == 0
        assert (PrivVal(1) - PrivValBool(1)).val() == 0
        assert (PrivValBool(1) - PrivVal(1)).val() == 0
        assert (1 - PrivValBool(1)).val() == 0
        assert (PrivValBool(1) - 1).val() == 0

    def test_not(self):
        assert (~PubValBool(0)).val() == 1
        assert (~PubValBool(1)).val() == 0

    def test_and(self):
        assert (PubValBool(0) & PubValBool(0)).val() == 0
        assert (PubValBool(0) & PubValBool(1)).val() == 0
        assert (PubValBool(1) & PubValBool(0)).val() == 0
        assert (PubValBool(1) & PubValBool(1)).val() == 1

    def test_or(self):
        assert (PubValBool(0) | PubValBool(0)).val() == 0
        assert (PubValBool(0) | PubValBool(1)).val() == 1
        assert (PubValBool(1) | PubValBool(0)).val() == 1
        assert (PubValBool(1) | PubValBool(1)).val() == 1

    def test_xor(self):
        assert (PubValBool(0) ^ PubValBool(0)).val() == 0
        assert (PubValBool(0) ^ PubValBool(1)).val() == 1
        assert (PubValBool(1) ^ PubValBool(0)).val() == 1
        assert (PubValBool(1) ^ PubValBool(1)).val() == 0
