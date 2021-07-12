import pysnark.runtime
from pysnark.runtime import LinComb, ConstVal, PrivVal, PubVal, add_constraint

"""
Support for Boolean values
Costs 1 constraint to convert a LinComb to a LinCombBool
"""

class LinCombBool:
    def __init__(self, lc, constrain=True):
        """
        Constructs a LinCombBool
        Costs 1 constraint
        """
        if not isinstance(lc, LinComb):
            raise RuntimeError("Wrong type for LinCombBool")
        if not LinCombBool.is_boolean_value(lc.value):
            raise ValueError("LinCombBool can only take Boolean values")
        
        # Add boolean constraint to circuit
        if constrain:
            add_constraint(lc, 1 - lc, LinComb.ZERO)
        
        self.lc = lc

    def val(self):
        return self.lc.val()

    def __repr__(self):
        return "{" + str(self.lc.value) + "}"

    @classmethod
    def is_boolean_value(cls, val):
        if val == 0 or val == 1 or val == True or val == False:
            return True
        return False

    @classmethod
    def parse_boolean(cls, val):
        if val == 0 or val == 1:
            return val
        if val == True:
            return 1
        if val == False:
            return 0
        raise ValueError("LinCombBool can only take Boolean values")

    @classmethod
    def _ensurebool(cls, val):
        if isinstance(val,LinCombBool):
            return val
        elif isinstance(val,LinComb):
            if not LinCombBool.is_boolean_value(val.value):
                raise ValueError("LinCombBool can only take Boolean values")
            return LinCombBool(val)
        elif isinstance(val, int):
            if not LinCombBool.is_boolean_value(val):
                raise ValueError("LinCombBool can only take Boolean values")
            return LinCombBool(ConstVal(val))
        raise RuntimeError("Wrong type for LinCombBool")
    
    def __add__(self, other):
        """
        Performs an arithmetic addition with an integer or a LinComb
        Returns a LinComb
        Costs 0 constraints
        """
        return self.lc + other

    def __sub__(self, other):
        """
        Performs an arithmetic subtraction by an integer or a LinComb
        Returns a LinComb
        Costs 0 constraints
        """
        return self.lc - other

    def __mul__(self, other):
        """
        Performs an arithmetic multiplication with an integer or a LinComb
        Returns a LinComb
        Costs 0 constraints to multiply with an integer
        Costs 1 constraint to multiply with a LinComb
        """
        return self.lc * (other)
    
    def __truediv__(self, other): 
        return NotImplemented
         
    def __floordiv__(self, other):
        return NotImplemented

    def __mod__(self, other):
        return NotImplemented
        
    def __divmod__(self, divisor):
        return NotImplemented

    __radd__ = __add__
    __rmul__ = __mul__

    def __rsub__(self, other):
        """
        Performs an arithmetic subtraction by an integer or a LinComb
        Returns a LinComb
        Costs 0 constraints
        """
        return other + (-self.lc)

    def __rtruediv__(self, other):
        return NotImplemented

    def __neg__(self):
        """
        Performs an arithmetic negation
        Returns a LinComb
        Costs 0 constraints
        """
        return -self.lc
    
    def __invert__(self):
        """
        Performs a logical not
        Returns a LinCombBool
        Costs 1 constraint
        """
        return LinCombBool(1 - self.lc, False)

    def __and__(self, other):
        """
        Performs a logical AND
        Costs 0 constraints to AND with a constant
        Costs 1 constraint to AND with a LinComb
        """
        if isinstance(other, int):
            return LinCombBool(self.lc * other, False)
        other = LinCombBool._ensurebool(other)
        return LinCombBool(self.lc * other.lc, False)

    def __xor__(self, other):
        """
        Performs a logical XOR
        Costs 0 constraints to XOR with a constant
        Costs 1 constraint to XOR with a LinComb
        """
        if isinstance(other, int):
            return LinCombBool(self + other - 2 * self * other, False)
        other = LinCombBool._ensurebool(other)
        return LinCombBool(self.lc + other.lc - 2 * self.lc * other.lc, False)

    def __or__(self, other):
        """
        Performs a logical OR
        Costs 0 constraints to OR with a constant
        Costs 1 constraint to OR with a LinComb
        """
        if isinstance(other, int):
            return LinCombBool(self.lc * other, False)
        other = LinCombBool._ensurebool(other)
        return LinCombBool(self.lc + other.lc - self.lc * other.lc, False)

    def __eq__(self, other): return self.lc == self._ensurebool(other).lc
    def __ne__(self, other): return self.lc != self._ensurebool(other).lc
    def __lt__(self, other): return self.lc < self._ensurebool(other).lc
    def __le__(self, other): return self.lc <= self._ensurebool(other).lc
    def __gt__(self, other): return self.lc > self._ensurebool(other).lc
    def __ge__(self, other): return self.lc >= self._ensurebool(other).lc
    
    def assert_eq(self, other, err=None): self.lc.assert_eq(self._ensurebool(other).lc)
    def assert_ne(self, other, err=None): self.lc.assert_ne(self._ensurebool(other).lc)
    def assert_lt(self, other, err=None): self.lc.assert_lt(self._ensurebool(other).lc)
    def assert_le(self, other, err=None): self.lc.assert_le(self._ensurebool(other).lc)
    def assert_gt(self, other, err=None): self.lc.assert_gt(self._ensurebool(other).lc)
    def assert_ge(self, other, err=None): self.lc.assert_ge(self._ensurebool(other).lc)
        
    def __bool__(self):
        raise NotImplementedError("Cannot call __bool__ on a LinComb. \
            Instead of if statements, use if_then_else from pysnark.branching")
        
    def __pow__(self, other, mod=None):
        """
        Raises a LinCombBool to the power of an integer, LinComb, or LinCombBool
        Returns a LinComb
        Costs 3 constraints
        """
        return self.lc != 0
    
    def __lshift__(self, other):
        return NotImplemented
    
    def __rshift__(self, other):
        return NotImplemented
        
    def __pos__(self):
        return self
    
    def __abs__(self):
        return self.lc.__abs__()

    def __int__(self):
        raise NotImplementedError("Should not run int() on LinCombBool")
        
    def check_positive(self): return self.lc.check_positive()
    def assert_positive(self): self.lc.assert_positive()
    def check_zero(self): return self.lc.check_zero()
    def assert_zero(self): self.lc.assert_zero()
    def assert_nonzero(self): self.lc.assert_nonzero()
        
def PubValBool(val):
    if not isinstance(val, int) and not isinstance(val, bool):
        raise RuntimeError("Wrong type for PubValBool")
    val = LinCombBool.parse_boolean(val)
    return LinCombBool(PubVal(val))

def PrivValBool(val):
    if not isinstance(val, int) and not isinstance(val, bool):
        raise RuntimeError("Wrong type for PrivValBool")
    val = LinCombBool.parse_boolean(val)
    return LinCombBool(PrivVal(val))