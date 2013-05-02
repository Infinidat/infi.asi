from infi.instruct import Struct, BitField, BitFields

# spc4r30: 4.3.5 (page 42)
class OperationCode(Struct):
    _fields_ = BitFields(
        BitField("command_code", 5),
        BitField("group_code", 3)
    )

    def __init__(self, opcode=None):
        super(OperationCode, self).__init__()
        if opcode is not None:
            self.command_code = opcode & 0x1f
            self.group_code = opcode >> 5

    COMMAND_SIZE_BY_GROUP_CODE = dict([
        [ 0, 6 ],
        [ 1, 10 ],
        [ 2, 10 ],
        [ 3, 0 ], # reserved (see opcode 7E and 7F in sections 4.3.3 and 4.3.4)
        [ 4, 16 ],
        [ 5, 12 ],
        [ 6, 0 ], # vendor-specific
        [ 7, 0 ] # vendor-specific
    ])

CDB_OPCODE_INQUIRY = 0x12
CDB_RECEIVE_DIAGNOSTIC_RESULTS = 0x1C
