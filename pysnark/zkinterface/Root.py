# automatically generated by the FlatBuffers compiler, do not modify

# namespace: zkinterface

import flatbuffers

class Root(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsRoot(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Root()
        x.Init(buf, n + offset)
        return x

    # Root
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Root
    def MessageType(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint8Flags, o + self._tab.Pos)
        return 0

    # Root
    def Message(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            from flatbuffers.table import Table
            obj = Table(bytearray(), 0)
            self._tab.Union(obj, o)
            return obj
        return None

def RootStart(builder): builder.StartObject(2)
def RootAddMessageType(builder, messageType): builder.PrependUint8Slot(0, messageType, 0)
def RootAddMessage(builder, message): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(message), 0)
def RootEnd(builder): return builder.EndObject()
