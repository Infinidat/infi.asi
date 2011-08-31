from infi.instruct import *

# sam5r07: 5.2 (page 70)
class Control(Struct):
    _fields_ = BitFields(
        BitPadding(2), # 0-1: obsolete
        BitField("naca", 1),
        BitPadding(3), # 3-5: reserved
        BitField("vendor_specific", 2), # 6-7: vendor specific
    )

DEFAULT_CONTROL = Control(vendor_specific=0, naca=0)
