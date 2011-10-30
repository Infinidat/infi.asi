from ... import SCSIReadCommand
from infi.instruct import UBInt8, UBInt16, UBInt32, UBInt64, BitFields, BitPadding, BitField, BitFlag, Struct
from infi.instruct import Padding, FixedSizeString, Lazy, Field, OptionalField
from . import InquiryCommand, PeripheralDeviceData

# spc4r30: 6.4.1 (page 259)
CDB_OPCODE_INQUIRY = 0x12

class StandardInquiryExtendedData(Struct):
    _fields_ = [
        FixedSizeString("vendor_specific", 20),
        BitFields(BitPadding(5), # reserved
                  BitFlag("ius"), # SPC-5 specific
                  BitFlag("qas"), # SPC-5 specific
                  BitFlag("clocking") # SPC-5 specific
        ),
        Padding(1), # reserved
        FixedSizeString("version_descriptors", 16),
        Padding(22)
    ]

# spc4r30: 6.4.2 (page 261)
class StandardInquiryData(Struct):
    def _is_extended_data_exist(self, stream, context):
        return self.additional_length >= StandardInquiryExtendedData.min_max_sizeof().max

    _fields_ = [
        Lazy(
            Field("peripheral_device", PeripheralDeviceData),
            BitFields(
                BitPadding(7),
                BitFlag("rmb"),
            ),
            UBInt8("version"),
            BitFields(
                BitField("response_data_format", 4),
                BitFlag("hisup"),
                BitFlag("normaca"),
                BitPadding(2), # 6-7: obsolete
            ),
            UBInt8("additional_length"),
            BitFields(
                BitFlag("protect"),
                BitPadding(2), # reserved
                BitFlag("3pc"),
                BitField("tpgs", 2),
                BitFlag("acc"),
                BitFlag("sccs"),
            ),
            BitFields(BitFlag("addr16"), # SPC-5 specific
                      BitPadding(3), # obsolete
                      BitFlag("multi_p"),
                      BitFlag("vs1"),
                      BitFlag("enc_serv"),
                      BitPadding(1)), # obsolete
            BitFields(BitFlag("vs2"),
                      BitFlag("cmd_que"),
                      BitPadding(2), # obsolete
                      BitFlag("sync"), # SPC-5 specific
                      BitFlag("wbus16"), # SPC-5 specific
                      BitPadding(2)), # obsolete
            FixedSizeString("t10_vendor_identification", 8),
            FixedSizeString("product_identification", 16),
            FixedSizeString("product_revision_level", 4),
        ),
        OptionalField("extended", StandardInquiryExtendedData, _is_extended_data_exist)
   ]

StandardInquiryDataLength = StandardInquiryData.min_max_sizeof().min + StandardInquiryExtendedData.min_max_sizeof().max

class StandardInquiryCommand(InquiryCommand):
    def __init__(self, page_code=0, evpd=0, allocation_length=StandardInquiryDataLength):
        super(StandardInquiryCommand, self).__init__(result_class=StandardInquiryData,
                                                     page_code=page_code, evpd=evpd,
                                                     allocation_length=allocation_length)
