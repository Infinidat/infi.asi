from infi.asi.cdb.inquiry import PeripheralDeviceDataBuffer
from infi.asi.cdb.inquiry.vpd_pages import EVPDInquiryCommand
from infi.instruct.buffer import Buffer, buffer_field, bytes_ref, be_uint_field, str_field, len_ref, self_ref, list_field
from infi.instruct.buffer.macros import b_uint8


class UnknownVPDPageBuffer(Buffer):
    peripheral_device = buffer_field(where=bytes_ref[0:], type=PeripheralDeviceDataBuffer)
    page_code = be_uint_field(where=bytes_ref[1])
    page_length = be_uint_field(where=bytes_ref[2:4], set_before_pack=len_ref(self_ref.page_data))
    page_data = list_field(where=bytes_ref[4:4+page_length], type=b_uint8)


# spc4r30: 7.8.15
def UnknownVPDPageCommand(page_code):
    class UnknownVPDPageCommand(EVPDInquiryCommand):
        def __init__(self):
            super(UnknownVPDPageCommand, self).__init__(page_code, 2048, UnknownVPDPageBuffer)
    return UnknownVPDPageCommand

__all__ = ["UnknownVPDPageCommand", "UnknownVPDPageBuffer"]
