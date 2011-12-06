from infi.instruct import Struct, Field, UBInt8, UBInt16, BitFields, BitField, BitPadding
from .. import PeripheralDeviceData
from . import EVPDInquiryCommand

class VeritasVPDPageData(Struct):
    _fields_ = [
        Field("peripheral_device", PeripheralDeviceData),
        UBInt8("page_code"),
        UBInt16("page_length"),
        BitFields(
                  BitField("is_thin_lun", 1),
                  BitField("is_snapshot_lun", 1),
                  BitField("is_space_optimized_src", 1),
                  BitField("is_fcdisk_lun", 1),
                  BitField("is_satadisk_lun", 1),
                  BitField("is_replication_src", 1),
                  BitField("is_replication_dst", 1),
                  BitPadding(1),
                  ),
        UBInt8("raid_type")]

# spc4r30: 7.8.15
class VeritasVPDPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(VeritasVPDPageCommand, self).__init__(0xc0, 255, VeritasVPDPageData)

__all__ = ["UnitSerialNumberVPDPageCommand", "UnitSerialNumberVPDPageData"]

