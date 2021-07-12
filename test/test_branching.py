import pytest
from pysnark.runtime import PrivVal
from pysnark.boolean import PrivValBool
from pysnark.fixedpoint import PrivValFxp
from pysnark.branching import if_then_else

class TestLinCombFxp():
    def test_lincomb_branch(self):
        assert if_then_else(PrivValBool(0), PrivVal(1), PrivVal(2)).val() == 2
        assert if_then_else(PrivValBool(1), PrivVal(1), PrivVal(2)).val() == 1

    def test_lincombbool_branch(self):
        assert if_then_else(PrivValBool(0), PrivValBool(1), PrivValBool(0)).val() == 0
        assert if_then_else(PrivValBool(1), PrivValBool(1), PrivValBool(0)).val() == 1

    def test_lincombfxp_branch(self):
        assert if_then_else(PrivValBool(0), PrivValFxp(1.5), PrivValFxp(2.5)).val() == 2.5
        assert if_then_else(PrivValBool(1), PrivValFxp(1.5), PrivValFxp(2.5)).val() == 1.5

    def test_mixed_branch(self):
        assert if_then_else(PrivValBool(0), PrivVal(1), PrivValFxp(2.5)).val() == 2.5
        assert if_then_else(PrivValBool(1), PrivValFxp(1.5), PrivValBool(1)).val() == 1.5
        assert if_then_else(PrivValBool(1), PrivValBool(1), PrivVal(2)).val() == 1

    def test_branch_condition(self):
        with pytest.raises(RuntimeError):
            if_then_else(PrivVal(True), PrivVal(1), PrivVal(2))
        with pytest.raises(RuntimeError):
            if_then_else(PrivVal(1), PrivVal(1), PrivVal(2))
        with pytest.raises(RuntimeError):
            if_then_else(PrivValFxp(1), PrivVal(1), PrivVal(2))