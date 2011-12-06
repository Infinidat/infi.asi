from infi.instruct import Struct, Field, UBInt8, UBInt16, UBInt32, UBInt64
from infi.instruct import BitFields, BitField, BitPadding, Padding
from .. import PeripheralDeviceData
from . import EVPDInquiryCommand

# spc3r26: 6.5.3 (page 241)
class BlockLimitsVPDPageData(Struct):
    _fields_ = [
        Field("peripheral_device", PeripheralDeviceData),
        UBInt8("page_code"),
        UBInt16("page_length"),
        BitFields(BitField("wsnz", 1),
                  BitPadding(7)
                  ),
        UBInt8("maximum_compare_and_write_length"),
        UBInt16("optimal_transfer_length_granularity"),
        UBInt32("maximum_transfer_length"),
        UBInt32("optimal_transfer_length"),
        UBInt32("maximum_prefetch_xdread_xdwrite_transfer_length"),
        UBInt32("maximum_unmap_lba_count"),
        UBInt32("maximum_unmap_block_descriptor_count"),
        UBInt32("optimal_unmap_granularity"),
        BitFields(BitField("unmap_granularity_alignment__high", 7),
                  BitField("ugavalid", 1),
                  BitField("unmap_granularity_alignment__low", 24)
                  ),
        UBInt64("maximum_write_same_length"),
        Padding(21),
    ]

class BlockLimitsPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(BlockLimitsPageCommand, self).__init__(0xb0, 255, BlockLimitsVPDPageData)

__all__ = ["BlockLimitsPageCommand", "BlockLimitsVPDPageData"]

