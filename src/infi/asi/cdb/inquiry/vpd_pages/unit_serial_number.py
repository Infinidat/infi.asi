from infi.asi.cdb.inquiry import PeripheralDeviceDataBuffer
from infi.asi.cdb.inquiry.vpd_pages import EVPDInquiryCommand
from infi.instruct.buffer import Buffer, buffer_field, bytes_ref, be_uint_field, str_field, len_ref, self_ref
from infi.instruct.buffer.macros import b_uint8


class UnitSerialNumberVPDPageBuffer(Buffer):
    peripheral_device = buffer_field(where=bytes_ref[0:], type=PeripheralDeviceDataBuffer)
    page_code = be_uint_field(where=bytes_ref[1])
    page_length = be_uint_field(where=bytes_ref[3], set_before_pack=len_ref(self_ref.product_serial_number))
    product_serial_number = str_field(where=bytes_ref[4:4+page_length])


# spc4r30: 7.8.15
class UnitSerialNumberVPDPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(UnitSerialNumberVPDPageCommand, self).__init__(0x80, 252, UnitSerialNumberVPDPageBuffer)

__all__ = ["UnitSerialNumberVPDPageCommand", "UnitSerialNumberVPDPageBuffer"]
