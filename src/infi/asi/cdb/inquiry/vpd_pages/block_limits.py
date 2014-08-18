from infi.asi.cdb.inquiry import PeripheralDeviceDataBuffer
from infi.asi.cdb.inquiry.vpd_pages import EVPDInquiryCommand
from infi.instruct.buffer import Buffer, buffer_field, bytes_ref, be_uint_field


# spc3r26: 6.5.3 (page 241)
class BlockLimitsVPDPageBuffer(Buffer):
    peripheral_device = buffer_field(where=bytes_ref[0:], type=PeripheralDeviceDataBuffer)
    page_code = be_uint_field(where=bytes_ref[1])
    page_length = be_uint_field(where=bytes_ref[2:4])
    wsnz = be_uint_field(where=bytes_ref[4].bits[0])
    maximum_compare_and_write_length = be_uint_field(where=bytes_ref[5])
    optimal_transfer_length_granularity = be_uint_field(where=bytes_ref[6:8])
    maximum_transfer_length = be_uint_field(where=bytes_ref[8:12])
    optimal_transfer_length = be_uint_field(where=bytes_ref[12:16])
    maximum_prefetch_xdread_xdwrite_transfer_length = be_uint_field(where=bytes_ref[16:20])
    maximum_unmap_lba_count = be_uint_field(where=bytes_ref[20:24])
    maximum_unmap_block_descriptor_count = be_uint_field(where=bytes_ref[24:28])
    optimal_unmap_granularity = be_uint_field(where=bytes_ref[28:32])
    unmap_granularity_alignment = be_uint_field(where=(bytes_ref[35] + bytes_ref[34] + bytes_ref[33] + bytes_ref[32].bits[0:7]))
    ugavalid = be_uint_field(where=bytes_ref[32].bits[7])
    maximum_write_same_length = be_uint_field(where=bytes_ref[36:44])


class BlockLimitsPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(BlockLimitsPageCommand, self).__init__(0xb0, 252, BlockLimitsVPDPageBuffer)


__all__ = ["BlockLimitsPageCommand", "BlockLimitsVPDPageBuffer"]

