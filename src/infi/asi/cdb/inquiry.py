from . import CDB
from .. import SCSIReadCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *

# spc4r30: 6.4.1 (page 259)
CDB_OPCODE_INQUIRY = 0x12

class StandardInquiryExtendedData(Struct):
    _fields_ = [
        String("vendor_specific", 20), 
        BitFields(BitPadding(5), # reserved
                  Flag("ius"), # SPC-5 specific
                  Flag("qas"), # SPC-5 specific
                  Flag("clocking") # SPC-5 specific
        ),
        Padding(1), # reserved
        String("version_descriptors", 16),
        Padding(22)
    ]

class StandardInquiryData(Struct):
    def _is_extended_data_exist(self, stream):
        return self.additional_length >= StandardInquiryExtendedData.sizeof()
    
    _fields_ = [
        Lazy(
            BitFields(
                BitField("peripheral_device_type", 5),  # 0-4
                BitField("peripheral_qualifier", 3),    # 5-7
            ),
            BitFields(
                BitPadding(7),
                Flag("rmb"),
            ),
            UBInt8("version"),
            BitFields(
                BitField("response_data_format", 4),
                Flag("hisup"),
                Flag("normaca"),
                BitPadding(2),      # 6-7: obsolete
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
            String("t10_vendor_identification", 8),
            String("product_identification", 16),
            String("product_revision_level", 4),
        ),
        OptionalField("extended", StandardInquiryExtendedData, _is_extended_data_exist)
   ]

StandardInquiryDataLength = StandardInquiryData.min_sizeof() + StandardInquiryExtendedData.sizeof()

class InquiryCommand(CDB):
    _fields_ = [
        ConstField("opcode", OperationCode(command_code=CDB_OPCODE_INQUIRY, group_code=0)),
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
    def __init__(self):
        super(StandardInquiryCommand, self).__init__()
        self.page_code = 0
        self.allocation_length = StandardInquiryDataLength

    def execute(self, executer):
        datagram = self.create_datagram()

        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.allocation_length))

        standard_inquiry_data = StandardInquiryData.create_instance_from_string(result_datagram)
        
        yield standard_inquiry_data
