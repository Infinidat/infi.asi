from infi.instruct import Struct, Field, UBInt8, UBInt16, UBInt32, Padding
from .. import PeripheralDeviceData
from . import EVPDInquiryCommand

class BlockLimitsVPDPageData(Struct):
    _fields_ = [
        Field("peripheral_device", PeripheralDeviceData),
        UBInt8("page_code"),
        UBInt16("page_length"),
        Padding(1),
        UBInt8("maximum_compare_and_write_length"),
        UBInt16("optimal_transfer_length_granularity"),
        UBInt32("maximum_transfer_length"),
        UBInt32("optimal_transfer_length"),
        UBInt32("maximum_prefetch_xdread_xdwrite_transfer_length"),
        UBInt32("maximum_unmap_lba_count"),
        UBInt32("maximum_unmap_block_descriptor_count"),
        UBInt32("optimal_unmap_granularity"),
        UBInt32("unmap_granularity_alignment")
    ]

class BlockLimitsPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(BlockLimitsPageCommand, self).__init__(0xb0, 255, BlockLimitsVPDPageData)

__all__ = ["UnitSerialNumberVPDPageCommand", "UnitSerialNumberVPDPageData"]

