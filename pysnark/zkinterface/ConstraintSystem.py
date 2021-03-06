# automatically generated by the FlatBuffers compiler, do not modify

# namespace: zkinterface

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

# ConstraintSystem represents constraints to be added to the constraint system.
#
# Multiple such messages are equivalent to the concatenation of `constraints` arrays.
class ConstraintSystem(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ConstraintSystem()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsConstraintSystem(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    @classmethod
    def ConstraintSystemBufferHasIdentifier(cls, buf, offset, size_prefixed=False):
        return flatbuffers.util.BufferHasIdentifier(buf, offset, b"\x7A\x6B\x69\x66", size_prefixed=size_prefixed)

    # ConstraintSystem
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # ConstraintSystem
    def Constraints(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from zkinterface.BilinearConstraint import BilinearConstraint
            obj = BilinearConstraint()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # ConstraintSystem
    def ConstraintsLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # ConstraintSystem
    def ConstraintsIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        return o == 0

    # Optional: Any complementary info that may be useful.
    #
    # Example: human-readable descriptions.
    # Example: custom hints to an optimizer or analyzer.
    # ConstraintSystem
    def Info(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from zkinterface.KeyValue import KeyValue
            obj = KeyValue()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # ConstraintSystem
    def InfoLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # ConstraintSystem
    def InfoIsNone(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        return o == 0

def Start(builder): builder.StartObject(2)
def ConstraintSystemStart(builder):
    """This method is deprecated. Please switch to Start."""
    return Start(builder)
def AddConstraints(builder, constraints): builder.PrependUOffsetTRelativeSlot(0, flatbuffers.number_types.UOffsetTFlags.py_type(constraints), 0)
def ConstraintSystemAddConstraints(builder, constraints):
    """This method is deprecated. Please switch to AddConstraints."""
    return AddConstraints(builder, constraints)
def StartConstraintsVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def ConstraintSystemStartConstraintsVector(builder, numElems):
    """This method is deprecated. Please switch to Start."""
    return StartConstraintsVector(builder, numElems)
def AddInfo(builder, info): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(info), 0)
def ConstraintSystemAddInfo(builder, info):
    """This method is deprecated. Please switch to AddInfo."""
    return AddInfo(builder, info)
def StartInfoVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def ConstraintSystemStartInfoVector(builder, numElems):
    """This method is deprecated. Please switch to Start."""
    return StartInfoVector(builder, numElems)
def End(builder): return builder.EndObject()
def ConstraintSystemEnd(builder):
    """This method is deprecated. Please switch to End."""
    return End(builder)