from infi.instruct import Struct, Field, UBInt8, UBInt16, VarSizeString
from .. import PeripheralDeviceData
from . import EVPDInquiryCommand

# spc4r30: 7.8.15 (page 641)
class UnitSerialNumberVPDPageData(Struct):
    _fields_ = [
        Field("peripheral_device", PeripheralDeviceData),
        UBInt8("page_code"),
        VarSizeString("product_serial_number", UBInt16)
   ]

# spc4r30: 7.8.15
class UnitSerialNumberVPDPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(UnitSerialNumberVPDPageCommand, self).__init__(0x80, 255, UnitSerialNumberVPDPageData)

__all__ = ["UnitSerialNumberVPDPageCommand", "UnitSerialNumberVPDPageData"]

