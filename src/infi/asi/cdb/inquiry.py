from . import CDB
from .. import SCSIReadCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import UBInt8, UBInt16, BitFields, BitPadding, BitField, Flag, Struct
from infi.instruct import Padding, FixedSizeString, Lazy, Field, OptionalField, ConstField
from infi.instruct.macros import VarSizeBuffer, SumSizeArray, StructFunc, SelectStructByFunc
from infi.instruct.struct.selector import FuncStructSelectorIO
from infi.instruct.errors import InstructError

# spc4r30: 6.4.1 (page 259)
CDB_OPCODE_INQUIRY = 0x12

class StandardInquiryExtendedData(Struct):
    _fields_ = [
        FixedSizeString("vendor_specific", 20),
        BitFields(BitPadding(5), # reserved
                  Flag("ius"), # SPC-5 specific
                  Flag("qas"), # SPC-5 specific
                  Flag("clocking") # SPC-5 specific
        ),
        Padding(1), # reserved
        FixedSizeString("version_descriptors", 16),
        Padding(22)
    ]

class PeripheralDevice(Struct):
    _fields_ = [
        BitFields(
            BitField("type", 5), # 0-4
            BitField("qualifier", 3), # 5-7
        )
    ]

class StandardInquiryData(Struct):
    def _is_extended_data_exist(self, stream, context):
        return self.additional_length >= StandardInquiryExtendedData.min_max_sizeof().max

    _fields_ = [
        Lazy(
            Field("peripheral_device", PeripheralDevice),
            BitFields(
                BitPadding(7),
                Flag("rmb"),
            ),
            UBInt8("version"),
            BitFields(
                BitField("response_data_format", 4),
                Flag("hisup"),
                Flag("normaca"),
                BitPadding(2), # 6-7: obsolete
            ),
            UBInt8("additional_length"),
            BitFields(
                Flag("protect"),
                BitPadding(2), # reserved
                Flag("3pc"),
                BitField("tpgs", 2),
                Flag("acc"),
                Flag("sccs"),
            ),
            BitFields(BitPadding(1), # obsolete
                      Flag("enc_serv"),
                      Flag("vs"),
                      Flag("multi_p"),
                      BitPadding(3), # obsolete
                      Flag("addr16")), # SPC-5 specific
            BitFields(BitPadding(2), # obsolete
                      Flag("wbus16"), # SPC-5 specific
                      Flag("sync"), # SPC-5 specific
                      BitPadding(2), # obsolete
                      Flag("cmd_que"),
                      Flag("vs")),
            FixedSizeString("t10_vendor_identification", 8),
            FixedSizeString("product_identification", 16),
            FixedSizeString("product_revision_level", 4),
        ),
        OptionalField("extended", StandardInquiryExtendedData, _is_extended_data_exist)
   ]

StandardInquiryDataLength = StandardInquiryData.min_max_sizeof().min + StandardInquiryExtendedData.min_max_sizeof().max

class SupportedVPDPagesData(Struct):
    _fields_ = [
        Field("peripheral_device", PeripheralDevice),
        UBInt8("page_code"),
        SumSizeArray("vpd_parameters", UBInt16, UBInt8)
    ]

class InquiryCommand(CDB):
    _fields_ = [
        ConstField("opcode", OperationCode(opcode=CDB_OPCODE_INQUIRY)),
        BitFields(
            Flag("evpd", default=0),
            BitPadding(7)
        ),
        UBInt8("page_code"),
        Padding(1),
        UBInt8("allocation_length"),
        Field("control", Control, DEFAULT_CONTROL)
    ]

class StandardInquiryCommand(InquiryCommand):
    def __init__(self, page_code=0, evpd=0, allocation_length=StandardInquiryDataLength):
        super(StandardInquiryCommand, self).__init__(page_code=page_code, evpd=evpd,
                                                     allocation_length=allocation_length)

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.allocation_length))
        standard_inquiry_data = StandardInquiryData.create_instance_from_string(result_datagram)

        yield standard_inquiry_data

class EVPDInquiryCommand(InquiryCommand):

    def __init__(self, page_code, allocation_length, result_class):
        super(EVPDInquiryCommand, self).__init__(page_code=page_code, evpd=1, allocation_length=allocation_length)
        self.result_class = result_class

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.allocation_length))
        result = self.result_class.create_from_string(result_datagram)
        yield result

# spc4r30: 7.82 (page 606)
class SupportedVPDPagesCommand(EVPDInquiryCommand):
    def __init__(self):
        super(SupportedVPDPagesCommand, self).__init__(0x00, 255, SupportedVPDPagesData)

# spc4r30: 7.8.15 (page 641)
class UnitSerialNumberVPDPageData(Struct):
    _fields_ = [
        Field("peripheral_device", PeripheralDevice),
        UBInt8("page_code"),
        VarSizeBuffer("product_serial_number", UBInt16)
   ]

# spc4r30: 7.8.15
class UnitSerialNumberVPDPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(UnitSerialNumberVPDPageCommand, self).__init__(0x80, 255, UnitSerialNumberVPDPageData)

DescriptorHeaderFieldsWithoutLength = [BitFields(BitField("code_set", 4),
                                                 BitField("designator_type", 4),
                                                 BitField("protocol_identifier", 4),
                                                 BitField("association", 2),
                                                 BitField("reserved", 1),
                                                 BitField("piv", 1),
                                                 BitPadding(8),
                                                 ),
                                       ]

DescriptorHeaderFields = DescriptorHeaderFieldsWithoutLength + [UBInt8("designator_length")]

class DescriptorHeader(Struct):
    _fields_ = DescriptorHeaderFields

# spc4r30: 7.8.15 (page 641)
class DeviceIdentificationVPDPageData(Struct):

    def _determine_designator(self, stream, context=None):
        header = DescriptorHeader.create_from_stream(stream, context)

        if header.designator_type == 0x00:
            class VendorSpecificDesignator(Struct):
                _fields_ = DescriptorHeaderFieldsWithoutLength + [VarSizeBuffer("vendor_specific_identifier", UBInt8)]
            return VendorSpecificDesignator

        if header.designator_type == 0x01:
            class T10VendorIDDesignator(Struct): # TODO this is ugly
                _fields_ = DescriptorHeaderFields + [FixedSizeString("t10_vendor_identification", 8),
                                                     FixedSizeString("vendor_specific_identifier",
                                                                     header.designator_length - 8)]
            return T10VendorIDDesignator

        if header.designator_type == 0x02:
            if header.designator_length == 0x08:
                class EUI64Designator(Struct):
                    _fields_ = DescriptorHeaderFields + \
                                [BitFields(BitField("ieee_company_id", 24),
                                           BitField("vendor_specific_extension_identifer", 40))]
                return EUI64Designator
            if header.designator_length == 0x0c:
                class EUI64Designator12Byte(Struct):
                    _fields_ = DescriptorHeaderFields + \
                                [BitFields(BitField("ieee_company_id", 24),
                                           BitField("vendor_specific_extension_identifer", 40),
                                           BitField("directory_id", 32))]
                return EUI64Designator12Byte
            if header.designator_length == 0x10:
                class EUI64Designator16Byte(Struct):
                    _fields_ = DescriptorHeaderFields + \
                                [BitFields(BitField("identifier_extension", 8),
                                           BitField("ieee_company_id", 24),
                                           BitField("vendor_specific_extension_identifer", 40))]
                return EUI64Designator16Byte
            raise InstructError("reserved designator length: %d" % header.designator_length)

        if header.designator_type == 0x03:
            NAAHeaderFields = DescriptorHeaderFields + \
                               [BitFields(BitField("naa_specific_data_high", 4),
                                          BitField("naa", 4))]
            class NAAHeader(Struct):
                _fields = NAAHeaderFields
            naa_header = NAAHeader.create_from_stream(stream, context)
            if naa_header.naa == 0x02:
                class NAAIEEEExtendedDesignator(Struct):
                    _fields_ = DescriptorHeaderFields + \
                                [BitFields(BitField("vendor_specific_identifer_a__high", 4),
                                           BitField("naa", 4),
                                           BitField("vendor_specific_identifier_a__low", 8),
                                           BitField("ieee_company_id", 24),
                                           BitField("vendor_specific_identifier_b__low", 24))]
                return NAAIEEEExtendedDesignator
            if naa_header.naa == 0x03:
                class NAALocallyAssignedDesignator(Struct):
                    _fields_ = DescriptorHeaderFields + \
                                [BitFields(BitField("locally_administered_value__high", 4),
                                           BitField("naa", 4),
                                           BitField("locally_administered_value__low", 7))]
                return NAALocallyAssignedDesignator
            if naa_header.naa == 0x05:
                class NAAIEEERegisteredDesignator(Struct):
                    _fields_ = DescriptorHeaderFields + \
                                [BitFields(BitField("ieee_company_id__high", 4),
                                           BitField("naa", 4),
                                           BitField("ieee_company_id__middle", 16),
                                           BitField("vendor_specific_identifier__high", 4),
                                           BitField("ieee_company_id__low", 4),
                                           BitField("vendor_specific_identifier__low", 32))]
                return NAAIEEERegisteredExtendedDesignator
            if naa_header.naa == 0x06:
                class NAAIEEERegisteredExtendedDesignator(Struct):
                    _fields_ = DescriptorHeaderFields + [BitFields("ieee_company_id__high", 4),
                                              BitFields("naa", 4),
                                              BitFields("ieee_company_id__middle", 16),
                                              BitFields("vendor_specific_identifier__high", 4),
                                              BitFields("ieee_company_id__low", 4),
                                              BitFields("vendor_specific_identifier__low", 32),
                                              BitFields("vendor_specific_identifier_extension", 64), ]
                return NAAIEEERegisteredExtendedDesignator
            raise InstructError("reserved naa field: %d" % naa_header.naa)

        if header.designator_type == 0x04:
            class RelativeTargetPortDesignator(Struct):
                _fields_ = DescriptorHeaderFields + [Padding(2),
                                                     UBInt16("relative_target_port_identifier")]
            return RelativeTargetPortDesignator
        if header.designator_type == 0x05:
            class TargetPortGroupDesignator(Struct):
                _fields_ = DescriptorHeaderFields + [Padding(2),
                                                     UBInt16("target_port_group")]
            return TargetPortGroupDesignator
        if header.designator_type == 0x06:
            class LogicalUnitGroupDesignator(Struct):
                _fields_ = DescriptorHeaderFields + [Padding(2),
                                                     UBInt16("logical_unit_group")]
            return LogicalUnitGroupDesignator
        if header.designator_type == 0x07:
            class MD5LogicalUnitDesignator(Struct):
                _fields_ = DescriptorHeaderFields + [Padding(2),
                                                     FixedSizeString("md5_logical_unit_identifier", 16)]
            return MD5LogicalUnitDesignator
        if header.designator_type == 0x08:
            class SCSINameDesignator(Struct):
                _fields_ = DescriptorHeaderFieldsWithoutLength + [VarSizeBuffer("scsi_name_string", UBInt8)]
            return SCSINameDesignator
        raise InstructError("unknown designator type: %d" % header.designator_type)

    _fields_ = [
        Field("peripheral_device", PeripheralDevice),
        UBInt8("page_code"),
        SumSizeArray("designators_list", UBInt16,
                     FuncStructSelectorIO(StructFunc(_determine_designator), (0, 255))),
]

# spc4r30: 7.8.5
class DeviceIdentificationVPDPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(DeviceIdentificationVPDPageCommand, self).__init__(0x83, 255, DeviceIdentificationVPDPageData)

INQUIRY_PAGE_SUPPORTED_VPD_PAGES = 0x00
INQUIRY_PAGE_UNIT_SERIAL_NUMBER = 0x80
INQUIRY_PAGE_DEVICE_IDENTIFICATION = 0x83

SUPPORTED_VPD_PAGES_COMMANDS = {
    INQUIRY_PAGE_SUPPORTED_VPD_PAGES: SupportedVPDPagesCommand,
    INQUIRY_PAGE_UNIT_SERIAL_NUMBER: UnitSerialNumberVPDPageCommand,
    INQUIRY_PAGE_DEVICE_IDENTIFICATION: DeviceIdentificationVPDPageCommand
}
