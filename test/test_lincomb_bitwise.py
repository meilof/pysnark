import pytest
from pysnark.runtime import PrivVal
from pysnark.boolean import LinCombBool

class TestLinCombBitwise():
    def test_to_bits(self):
        bits = PrivVal(5).to_bits()
        assert bits[3].val() == 0
        assert bits[2].val() == 1
        assert bits[1].val() == 0
        assert bits[0].val() == 1

    def test_and(self):
        assert (3 & PrivVal(7)).val() == 3
        assert (PrivVal(7) & 3).val() == 3
        assert (PrivVal(7) & PrivVal(3)).val() == 3
        assert (PrivVal(7) & PrivVal(0)).val() == 0
        assert (PrivVal(0) & PrivVal(7)).val() == 0

    def test_or(self):
        assert (3 | PrivVal(7)).val() == 7
        assert (PrivVal(7) | 3).val() == 7
        assert (PrivVal(7) | PrivVal(3)).val() == 7
        assert (PrivVal(7) | PrivVal(0)).val() == 7
        assert (PrivVal(0) | PrivVal(7)).val() == 7

    def test_xor(self):
        assert (3 ^ PrivVal(7)).val() == 4
        assert (PrivVal(7) ^ 3).val() == 4
        assert (PrivVal(7) ^ PrivVal(3)).val() == 4
        assert (PrivVal(7) ^ PrivVal(0)).val() == 7
        assert (PrivVal(0) ^ PrivVal(7)).val() == 7
        