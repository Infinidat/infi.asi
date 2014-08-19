from infi.asi.cdb.inquiry import PeripheralDeviceDataBuffer
from infi.asi.cdb.inquiry.vpd_pages import EVPDInquiryCommand
from infi.instruct.buffer import Buffer, bytes_ref, buffer_field, be_uint_field, input_buffer_length
from .designators import DesignatorDescriptor, determine_designator


# sbc4r02: 6.6.5 (page 303)
class LogicalBlockProvisioningVPDPageBuffer(Buffer):
    peripheral_device = buffer_field(where=bytes_ref[0:], type=PeripheralDeviceDataBuffer)
    page_code = be_uint_field(where=bytes_ref[1])
    page_length = be_uint_field(where=bytes_ref[2:4])

    threshold_exponent = be_uint_field(where=bytes_ref[4])
    # bit-field
    dp = be_uint_field(where=bytes_ref[5].bits[0])
    anc_sup = be_uint_field(where=bytes_ref[5].bits[1])
    lbprz = be_uint_field(where=bytes_ref[5].bits[2])
    # reserved
    lbpws10 = be_uint_field(where=bytes_ref[5].bits[5])
    lbpws = be_uint_field(where=bytes_ref[5].bits[6])
    lbpu = be_uint_field(where=bytes_ref[5].bits[7])
    provisioning_type = be_uint_field(where=bytes_ref[6].bits[0:3])
    # reserved
    provisioning_group_descriptor = buffer_field(where=bytes_ref[8:], type=DesignatorDescriptor,
                                                 unpack_selector=determine_designator,
                                                 unpack_if=input_buffer_length>8)


class LogicalBlockProvisioningPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(LogicalBlockProvisioningPageCommand, self).__init__(0xb2, 252, LogicalBlockProvisioningVPDPageBuffer)


__all__ = ["LogicalBlockProvisioningPageCommand", "LogicalBlockProvisioningVPDPageBuffer"]
