from infi.asi.cdb.read import SCSIReadCommand
from infi.instruct.buffer import (Buffer, buffer_field, bytes_ref, int_field, uint_field, str_field, bytearray_field,
                                  b_uint16, input_buffer_length, min_ref, list_field, self_ref)
from . import InquiryCommand, PeripheralDeviceDataBuffer

# spc4r30: 6.4.1 (page 259)
CDB_OPCODE_INQUIRY = 0x12


class StandardInquiryExtendedDataBuffer(Buffer):
    vendor_specific_1 = bytearray_field(where_when_unpack=bytes_ref[0:min_ref(20, input_buffer_length)],
                                        where_when_pack=bytes_ref[0:])
    # SPC-5 specific
    ius = uint_field(where=bytes_ref[20].bits[0],
                     unpack_if=input_buffer_length >= 21)
    # SPC-5 specific
    qas = uint_field(where=bytes_ref[20].bits[1],
                     unpack_if=input_buffer_length >= 21)
    # SPC-5 specific
    clocking = uint_field(where=bytes_ref[20].bits[2:4],
                          unpack_if=input_buffer_length >= 21)
    # bytes_ref[20].bits[4:8] - reserved
    # bytes_ref[21] - reserved
    version_descriptors = list_field(type=b_uint16,
                                     where=bytes_ref[22:],
                                     n=min_ref((input_buffer_length - 22) // 2, 8),  # / 2 because sizeof(uint16) == 2
                                     unpack_if=input_buffer_length >= 24)
    # bytes_ref[38:60] - reserved
    vendor_specific_2 = bytearray_field(where=bytes_ref[60:], unpack_if=input_buffer_length >= 61,
                                        pack_if=self_ref._has_vendor_specific_2_data())

    def _has_vendor_specific_2_data(self):
        return self.vendor_specific_2 is not None


# spc4r30: 6.4.2 (page 261)
class StandardInquiryDataBuffer(Buffer):
    peripheral_device = buffer_field(PeripheralDeviceDataBuffer, where=bytes_ref[0])
    # bytes_ref[1].bits[0:7] - reserved
    rmb = uint_field(where=bytes_ref[1].bits[7])
    version = uint_field(where=bytes_ref[2])
    response_data_format = uint_field(where=bytes_ref[3].bits[0:4])
    hisup = uint_field(where=bytes_ref[3].bits[4])
    normaca = uint_field(where=bytes_ref[3].bits[5])
    # bytes_ref[3].bits[6:8] - obsolete
    additional_length = uint_field(where=bytes_ref[4],
                                   set_before_pack=self_ref._calc_additional_length())
    protect = uint_field(where=bytes_ref[5].bits[0])
    # bytes_ref[5].bits[1:3] - reserved
    threepc = uint_field(where=bytes_ref[5].bits[3])
    tpgs = uint_field(where=bytes_ref[5].bits[4:6])
    acc = uint_field(where=bytes_ref[5].bits[6])
    sccs = uint_field(where=bytes_ref[5].bits[7])

    addr16 = uint_field(where=bytes_ref[6].bits[0])  # SPC-5 specific
    # bytes_ref[6].bits[1:4] - obsolete
    multi_p = uint_field(where=bytes_ref[6].bits[4])
    # bytes_ref[6].bits[5] - VS
    enc_serv = uint_field(where=bytes_ref[6].bits[6])
    # bytes_ref[6].bits[7] - obsolete
    # bytes_ref[7].bits[0] - VS
    cmd_que = uint_field(where=bytes_ref[7].bits[1])
    # bytes_ref[7].bits[2:4] - obsolete
    sync = uint_field(where=bytes_ref[7].bits[4])  # SPC-5 specific
    wbus16 = uint_field(where=bytes_ref[7].bits[5])  # SPC-5 specific
    # bytes_ref[7].bits[6:8] - obsolete
    t10_vendor_identification = str_field(where=bytes_ref[8:16], padding=b' ', justify='left')
    product_identification = str_field(where=bytes_ref[16:32], padding=b' ', justify='left')
    product_revision_level = str_field(where=bytes_ref[32:36], padding=b' ', justify='left')

    extended = buffer_field(StandardInquiryExtendedDataBuffer,
                            where=bytes_ref[36:additional_length + 5],
                            pack_if=self_ref._has_extended_data(),
                            unpack_if=additional_length > (36 - 5))

    def _has_extended_data(self):
        return self.extended is not None

    def _calc_additional_length(self):
        additional_length = 36 - 5  # SCSI's definition: additional length = n - 4
        if self.extended is not None:
            additional_length += len(self.extended.pack())
        return additional_length


# spc4r18
STANDARD_INQUIRY_MINIMAL_DATA_LENGTH = 36 # The standard INQUIRY data (see table 131) shall contain at least 36 bytes.


class StandardInquiryCommand(InquiryCommand):
    def __init__(self, page_code=0, evpd=0, allocation_length=STANDARD_INQUIRY_MINIMAL_DATA_LENGTH):
        super(StandardInquiryCommand, self).__init__(result_class=StandardInquiryDataBuffer,
                                                     page_code=page_code, evpd=evpd,
                                                     allocation_length=allocation_length)
