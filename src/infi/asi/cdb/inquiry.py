from . import CDB
from .. import SCSIReadCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *
from infi.instruct.macros import VarSizeBuffer

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

class UnitSerialNumberVPDPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(UnitSerialNumberVPDPageCommand, self).__init__(0x80, 255, UnitSerialNumberVPDPageData)

INQUIRY_PAGE_SUPPORTED_VPD_PAGES = 0x00
INQUIRY_PAGE_UNIT_SERIAL_NUMBER = 0x80
INQUIRY_PAGE_DEVICE_IDENTIFICATION = 0x83

SUPPORTED_VPD_PAGES_COMMANDS = {
    INQUIRY_PAGE_SUPPORTED_VPD_PAGES: SupportedVPDPagesCommand,
    INQUIRY_PAGE_UNIT_SERIAL_NUMBER: UnitSerialNumberVPDPageCommand
}
