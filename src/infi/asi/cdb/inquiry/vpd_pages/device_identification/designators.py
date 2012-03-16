from infi.instruct import UBInt8, UBInt16, UBInt32, UBInt64, BitFields, BitPadding, BitField, Struct
from infi.instruct import Padding, FixedSizeString
from infi.instruct.macros import VarSizeString, ReadPointer, CallableReader, StructFunc

DescriptorHeaderFieldsWithoutLength = [BitFields(BitField("code_set", 4),
                                                 BitField("protocol_identifier", 4),
                                                 BitField("designator_type", 4),
                                                 BitField("association", 2),
                                                 BitField("reserved", 1),
                                                 BitField("piv", 1),
                                                 BitPadding(8),
                                                 )]

DescriptorHeaderFields = DescriptorHeaderFieldsWithoutLength + [UBInt8("designator_length")]

# spc4r30, section 7.8.5.1, page 612
class DescriptorHeader(Struct):
    _fields_ = DescriptorHeaderFields

# spc4r30, section 7.8.5.1, page 612
# Designator types 09-0F are reserved
class Reserved_Designator(Struct):
    _fields_ = DescriptorHeaderFields + [ VarSizeString("designator", ReadPointer("designator_length")) ]

# spc4r30, section 7.8.5.5.2, page 617
class EUI64_Designator(Struct):
    _fields_ = DescriptorHeaderFields + \
                [BitFields(BitField("ieee_company_id", 24),
                           BitField("vendor_specific_extension_identifer", 40))]

# spc4r30, section 7.8.5.5.3, page 617
class EUI64_12Byte_Designator(Struct):
    _fields_ = DescriptorHeaderFields + \
                [BitFields(BitField("ieee_company_id", 24),
                           BitField("vendor_specific_extension_identifer", 40),
                           BitField("directory_id", 32))]

# spc4r30, section 7.8.5.5.4, page 618
class EUI64_16Byte_Designator(Struct):
    _fields_ = DescriptorHeaderFields + \
                [BitFields(BitField("identifier_extension", 8),
                           BitField("ieee_company_id", 24),
                           BitField("vendor_specific_extension_identifer", 40))]

# spc4r30, section 7.8.5.6.1, page 618
class NAA_Header(Struct):
    _fields_ = [BitFields(BitField("naa_specific_data_high", 4), BitField("naa", 4))]

# spc4r30, section 7.8.5.6.2, page 619
class NAA_IEEE_Extended_Designator(Struct):
    _fields_ = DescriptorHeaderFields + \
                [BitFields(BitField("vendor_specific_identifer_a__high", 4),
                           BitField("naa", 4),
                           BitField("vendor_specific_identifier_a__low", 8),
                           BitField("ieee_company_id", 24),
                           BitField("vendor_specific_identifier_b__low", 24))]

# spc4r30, section 7.8.5.6.2, page 619
class NAA_Locally_Assigned_Designator(Struct):
    _fields_ = DescriptorHeaderFields + \
                [BitFields(BitField("locally_administered_value__high", 4),
                           BitField("naa", 4),
                           BitField("locally_administered_value__low", 56))]

# spc4r30, section 7.8.5.6.4, page 620
class NAA_IEEE_Registered_Designator(Struct):
    _fields_ = DescriptorHeaderFields + \
                [BitFields(BitField("ieee_company_id__high", 4),
                           BitField("naa", 4)),
                 UBInt16("ieee_company_id__middle"),
                 BitFields(BitField("vendor_specific_identifier__high", 4),
                           BitField("ieee_company_id__low", 4)),
                 UBInt32("vendor_specific_identifier__low")]

# spc4r30, section 7.8.5.6.5, page 620
class NAA_IEEE_Registered_Extended_Designator(Struct):
    _fields_ = DescriptorHeaderFields + \
                [BitFields(BitField("ieee_company_id__high", 4),
                           BitField("naa", 4)),
                 UBInt16("ieee_company_id__middle"),
                 BitFields(BitField("vendor_specific_identifier__high", 4),
                           BitField("ieee_company_id__low", 4)),
                 UBInt32("vendor_specific_identifier__low"),
                 UBInt64("vendor_specific_identifier_extension")]

# spc4r30, section 7.8.5.7, page 621
class RelativeTargetPortDesignator(Struct):
    _fields_ = DescriptorHeaderFields + [Padding(2), UBInt16("relative_target_port_identifier")]

# spc4r30, section 7.8.5.8, page 622
class TargetPortGroupDesignator(Struct):
    _fields_ = DescriptorHeaderFields + [Padding(2), UBInt16("target_port_group")]

# spc4r30, section 7.8.5.9, page 622
class LogicalUnitGroupDesignator(Struct):
    _fields_ = DescriptorHeaderFields + [Padding(2), UBInt16("logical_unit_group")]

# spc4r30, section 7.8.5.10, page 622
class MD5LogicalUnitDesignator(Struct):
    _fields_ = DescriptorHeaderFields + [Padding(2), FixedSizeString("md5_logical_unit_identifier", 16)]

# spc4r30, section 7.8.5.11, page 624
class SCSINameDesignator(Struct):
    _fields_ = DescriptorHeaderFields + [VarSizeString("scsi_name_string", ReadPointer("designator_length"))]

# spc4r30, section 7.8.5.2.4, page 615
class VendorSpecificDesignator(Struct):
    _fields_ = DescriptorHeaderFields + [VarSizeString("vendor_specific_identifier", ReadPointer("designator_length"))]

class T10VendorIDDesignator(Struct):
    def _calc_vendor_specific_identifier_size(self, stream, context):
        return self.designator_length - 8
    
    _fields_ = DescriptorHeaderFields + \
               [ FixedSizeString("t10_vendor_identification", 8),
                 VarSizeString("vendor_specific_identifier",
                               CallableReader(StructFunc(_calc_vendor_specific_identifier_size))) ]

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
