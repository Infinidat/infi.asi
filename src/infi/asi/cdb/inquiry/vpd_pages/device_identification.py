from infi.asi.cdb.inquiry import PeripheralDeviceDataBuffer
from infi.asi.cdb.inquiry.vpd_pages import EVPDInquiryCommand
from infi.instruct.buffer import Buffer, buffer_field, list_field, bytes_ref, be_uint_field, len_ref, self_ref
from .designators import DesignatorDescriptor, determine_designator


# spc4r30: 7.8.15 (page 641)
class DeviceIdentificationVPDPageBuffer(Buffer):
    peripheral_device = buffer_field(where=bytes_ref[0:], type=PeripheralDeviceDataBuffer)
    page_code = be_uint_field(where=bytes_ref[1])
    page_length = be_uint_field(where=bytes_ref[2:4])
    designators_list = list_field(where=bytes_ref[4:4+page_length], type=DesignatorDescriptor,
                                  unpack_selector=determine_designator, unpack_after=page_length)


# spc4r30: 7.8.5
class DeviceIdentificationVPDPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(DeviceIdentificationVPDPageCommand, self).__init__(0x83, 252, DeviceIdentificationVPDPageBuffer)


__all__ = ["DeviceIdentificationVPDPageCommand", "DeviceIdentificationVPDPageBuffer"]
