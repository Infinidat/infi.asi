from infi.instruct.buffer import Buffer, be_uint_field, bytes_ref, str_field, len_ref, self_ref, bytearray_field, buffer_field
from infi.instruct.errors import InstructError
from logging import getLogger
logger = getLogger(__name__)


# spc4r30, section 7.8.5.1, page 612
class DesignatorDescriptor(Buffer):
    code_set = be_uint_field(where=bytes_ref[0].bits[0:4])
    protocol_identifier = be_uint_field(where=bytes_ref[0].bits[4:8])
    designator_type = be_uint_field(where=bytes_ref[1].bits[0:4])
    association = be_uint_field(where=bytes_ref[1].bits[4:6])
    piv = be_uint_field(where=bytes_ref[1].bits[7])
    reserved = be_uint_field(where=bytes_ref[2])
    designator_length = be_uint_field(where=bytes_ref[3])


# spc4r30, section 7.8.5.1, page 612
# Designator types 09-0F are reserved
class Reserved_Designator(DesignatorDescriptor):
    designator_length = be_uint_field(where=bytes_ref[3], set_before_pack=len_ref(self_ref.designator))
    desginator = str_field(where=bytes_ref[4:4+designator_length])


# spc4r30, section 7.8.5.5.2, page 617
class EUI64_Designator(DesignatorDescriptor):
    ieee_company = be_uint_field(where=bytes_ref[4:7])
    vendor_specific_extension_identifer = be_uint_field(where=bytes_ref[7:12])


# spc4r30, section 7.8.5.5.3, page 617
class EUI64_12Byte_Designator(EUI64_Designator):
    directory_id = be_uint_field(where=bytes_ref[12:16])


# spc4r30, section 7.8.5.5.4, page 618
class EUI64_16Byte_Designator(DesignatorDescriptor):
    identifier_extension = be_uint_field(where=bytes_ref[4:12])
    ieee_company = be_uint_field(where=bytes_ref[12:15])
    vendor_specific_extension_identifer = be_uint_field(where=bytes_ref[15:20])


# spc4r30, section 7.8.5.6.1, page 618
class NAA_Descriptor(DesignatorDescriptor):
    naa = be_uint_field(where=bytes_ref[4].bits[4:8])


# spc4r30, section 7.8.5.6.2, page 619
class NAA_IEEE_Extended_Designator(NAA_Descriptor):
    vendor_specific_identifier_a = be_uint_field(where=(bytes_ref[5] + bytes_ref[4].bits[0:4]))
    ieee_company = be_uint_field(where=bytes_ref[6:9])
    vendor_specific_identifier_b = be_uint_field(where=bytes_ref[9:12])


# spc4r30, section 7.8.5.6.2, page 619
class NAA_Locally_Assigned_Designator(NAA_Descriptor):
    locally_administered_value = be_uint_field(where=(bytes_ref[11] + bytes_ref[10] + bytes_ref[9] +
                                                      bytes_ref[8] + bytes_ref[7] + bytes_ref[6] + bytes_ref[5] +
                                                      bytes_ref[4].bits[0:4]))


# spc4r30, section 7.8.5.6.4, page 620
class NAA_IEEE_Registered_Designator(NAA_Descriptor):
    ieee_company_id = be_uint_field(where=(bytes_ref[7].bits[4:8] + bytes_ref[6] + bytes_ref[5] +
                                           bytes_ref[4].bits[0:4]))
    vendor_specific_identifier = be_uint_field(where=(bytes_ref[11] + bytes_ref[10] + bytes_ref[9] +
                                                      bytes_ref[8] + bytes_ref[7].bits[0:4]))


# spc4r30, section 7.8.5.6.5, page 620
class NAA_IEEE_Registered_Extended_Designator(NAA_IEEE_Registered_Designator):
    vendor_specific_identifier_extension = be_uint_field(where=bytes_ref[12:20])


# spc4r30, section 7.8.5.7, page 621
class RelativeTargetPortDesignator(DesignatorDescriptor):
    relative_target_port_identifier = be_uint_field(where=bytes_ref[6:8])


# spc4r30, section 7.8.5.8, page 622
class TargetPortGroupDesignator(DesignatorDescriptor):
    target_port_group = be_uint_field(where=bytes_ref[6:8])


# spc4r30, section 7.8.5.9, page 622
class LogicalUnitGroupDesignator(DesignatorDescriptor):
    logical_unit_group = be_uint_field(where=bytes_ref[6:8])


# spc4r30, section 7.8.5.10, page 622
class MD5LogicalUnitDesignator(DesignatorDescriptor):
    md5_logical_unit_identifier = bytearray_field(where=bytes_ref[6:8])


# spc4r30, section 7.8.5.11, page 624
class SCSINameDesignator(DesignatorDescriptor):
    designator_length = be_uint_field(where=bytes_ref[3], set_before_pack=len_ref(self_ref.scsi_name_string))
    scsi_name_string = bytearray_field(where=bytes_ref[4:4+designator_length])


# spc4r30, section 7.8.5.2.4, page 615
class VendorSpecificDesignator(DesignatorDescriptor):
    designator_length = be_uint_field(where=bytes_ref[3], set_before_pack=len_ref(self_ref.vendor_specific_identifier))
    vendor_specific_identifier = bytearray_field(where=bytes_ref[4:4+designator_length])


class T10VendorIDDesignator(DesignatorDescriptor):
    designator_length = be_uint_field(where=bytes_ref[3], set_before_pack=len_ref(self_ref.vendor_specific_identifier))
    t10_vendor_identification = str_field(where=bytes_ref[4:12])
    vendor_specific_identifier = bytearray_field(where=bytes_ref[12:4+designator_length])


EUI64_BY_LENGTH = {
                   0x08: EUI64_Designator,
                   0x0c: EUI64_12Byte_Designator,
                   0x10: EUI64_16Byte_Designator
                   }

NAA_BY_TYPE = {
               0x02: NAA_IEEE_Extended_Designator,
               0x03: NAA_Locally_Assigned_Designator,
               0x05: NAA_IEEE_Registered_Designator,
               0x06: NAA_IEEE_Registered_Extended_Designator,
               }

SINGLE_TYPE_DESIGNATORS = {
                           0x00: VendorSpecificDesignator,
                           0x01: T10VendorIDDesignator,
                           0x04: RelativeTargetPortDesignator,
                           0x05: TargetPortGroupDesignator,
                           0x06: LogicalUnitGroupDesignator,
                           0x07: MD5LogicalUnitDesignator,
                           0x08: SCSINameDesignator,
                           }


def _determine_eui_designator(header):
    key = header.designator_length
    if key in EUI64_BY_LENGTH:
        return EUI64_BY_LENGTH[key]
    raise InstructError("unknown reserved designator length: %r" % header)


def _determine_naa_designator(buffer):
    naa_header = NAA_Descriptor()
    naa_header.unpack(buffer.to_bytes())
    if naa_header.naa in NAA_BY_TYPE:
        return NAA_BY_TYPE[naa_header.naa]
    raise InstructError("unknown reserved naa field: %d" % naa_header.naa)


def determine_designator(instance, buffer, *args, **kwargs):
    header = DesignatorDescriptor()
    header.unpack(buffer.to_bytes())
    try:
        if header.designator_type in SINGLE_TYPE_DESIGNATORS:
            return SINGLE_TYPE_DESIGNATORS[header.designator_type]
        if header.designator_type == 0x02:
            return _determine_eui_designator(header)
        if header.designator_type == 0x03:
            return _determine_naa_designator(buffer)
        if header.designator_type >= 0x09 and header.designator_type <= 0x0F:
            # Reserved designator, we ignore it.
            return Reserved_Designator
        raise InstructError("unknown designator type: %r" % header)
    except:
        logger.exception("failed to determine designator for buffer {!r} / header {!r}".format(buffer, header))
        raise
