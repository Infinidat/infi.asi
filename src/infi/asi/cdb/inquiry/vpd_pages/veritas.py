from infi.asi.cdb.inquiry import PeripheralDeviceDataBuffer
from infi.asi.cdb.inquiry.vpd_pages import EVPDInquiryCommand
from infi.instruct.buffer import Buffer, buffer_field, bytes_ref, be_uint_field, str_field, len_ref, self_ref, list_field
from infi.instruct.buffer.macros import b_uint8


class VeritasVPDPageBuffer(Buffer):
    peripheral_device = buffer_field(where=bytes_ref[0:], type=PeripheralDeviceDataBuffer)
    page_code = be_uint_field(where=bytes_ref[1])
    page_length = be_uint_field(where=bytes_ref[2:4])

    is_thin_lun = be_uint_field(where=bytes_ref[4].bits[0])
    is_snapshot_lun = be_uint_field(where=bytes_ref[4].bits[1])
    is_space_optimized_src = be_uint_field(where=bytes_ref[4].bits[2])
    is_fcdisk_lun = be_uint_field(where=bytes_ref[4].bits[3])
    is_satadisk_lun = be_uint_field(where=bytes_ref[4].bits[4])
    is_replication_src = be_uint_field(where=bytes_ref[4].bits[5])
    is_replication_dst = be_uint_field(where=bytes_ref[4].bits[6])
    raid_type = be_uint_field(where=bytes_ref[5])


# spc4r30: 7.8.15
class VeritasVPDPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(VeritasVPDPageCommand, self).__init__(0xc0, 252, VeritasVPDPageBuffer)

__all__ = ["UnitSerialNumberVPDPageCommand", "UnitSerialNumberVPDPageData"]
