from infi.instruct import *
from infi.instruct.buffer import Buffer, bytes_ref, be_int_field


# sam5r07: 5.2 (page 70)
class Control(Struct):
    _fields_ = BitFields(
        BitPadding(2),  # 0-1: obsolete
        BitField("naca", 1),
        BitPadding(3),  # 3-5: reserved
        BitField("vendor_specific", 2),  # 6-7: vendor specific
    )

DEFAULT_CONTROL = Control(vendor_specific=0, naca=0)


class ControlBuffer(Buffer):
    naca = be_int_field(where=bytes_ref[0].bits[2:3])
    vendor_specific = be_int_field(where=bytes_ref[0].bits[6:8])

DEFAULT_CONTROL_BUFFER = ControlBuffer(vendor_specific=0, naca=0)
