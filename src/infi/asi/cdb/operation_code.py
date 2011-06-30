from infi.instruct import *

# spc4r30: 4.3.5 (page 42)
class OperationCode(Struct):
    _fields_ = BitFields(
        BitField("command_code", 5),
        BitField("group_code", 3)
    )
    
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
