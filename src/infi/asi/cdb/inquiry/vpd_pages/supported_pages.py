from infi.instruct import UBInt8, UBInt16, Struct, Field
from infi.instruct.macros import SumSizeArray
from .. import PeripheralDeviceData
from . import EVPDInquiryCommand

class SupportedVPDPagesData(Struct):
    _fields_ = [
        Field("peripheral_device", PeripheralDeviceData),
        UBInt8("page_code"),
        SumSizeArray("vpd_parameters", UBInt16, UBInt8)
    ]

# spc4r30: 7.82 (page 606)
class SupportedVPDPagesCommand(EVPDInquiryCommand):
    def __init__(self):
        super(SupportedVPDPagesCommand, self).__init__(0x00, 255, SupportedVPDPagesData)

__all__ = ["SupportedVPDPagesCommand, SupportedVPDPagesData"]
