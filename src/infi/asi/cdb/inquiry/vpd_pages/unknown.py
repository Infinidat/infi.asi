from infi.instruct import Struct, Field, UBInt8, UBInt16, VarSizeBuffer
from .. import PeripheralDeviceData
from . import EVPDInquiryCommand

# spc4r30: 7.8.15 (page 641)
class UnknownVPDPageData(Struct):
    _fields_ = [
        Field("peripheral_device", PeripheralDeviceData),
        UBInt8("page_code"),
        VarSizeBuffer("page_data", UBInt16)
   ]

# spc4r30: 7.8.15
def UnknownVPDPageCommand(page_code):
    class UnknownVPDPageCommand(EVPDInquiryCommand):
        def __init__(self):
            super(UnknownVPDPageCommand, self).__init__(page_code, 2048, UnknownVPDPageData)
    return UnknownVPDPageCommand

__all__ = ["UnknownVPDPageCommand", "UnknownVPDPageData"]

