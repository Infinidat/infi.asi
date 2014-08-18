from infi.asi.cdb.inquiry import PeripheralDeviceDataBuffer
from infi.asi.cdb.inquiry.vpd_pages import EVPDInquiryCommand
from infi.instruct.buffer import Buffer, buffer_field, bytes_ref, be_uint_field, list_field
from infi.instruct.buffer.macros import b_uint8


class SupportedVPDPagesBuffer(Buffer):
    peripheral_device = buffer_field(where=bytes_ref[0:], type=PeripheralDeviceDataBuffer)
    page_code = be_uint_field(where=bytes_ref[1])
    page_length = be_uint_field(where=bytes_ref[3])

    vpd_parameters = list_field(where=bytes_ref[4:], type=b_uint8, n=page_length)


# spc4r30: 7.82 (page 606)
class SupportedVPDPagesCommand(EVPDInquiryCommand):
    def __init__(self):
        super(SupportedVPDPagesCommand, self).__init__(0x00, 252, SupportedVPDPagesBuffer)


__all__ = ["SupportedVPDPagesCommand", "SupportedVPDPagesBuffer"]
