from infi.instruct import *

from .asc import AdditionalSenseCode

# spc4r30: 4.5.6 (page 59)
SCSI_SENSE_KEY = dict(NO_SENSE          = 0x00,
                      RECOVERED_ERROR   = 0x01,
                      NOT_READY         = 0x02,
                      MEDIUM_ERROR      = 0x03,
                      HARDWARE_ERROR    = 0x04,
                      ILLEGAL_REQUEST   = 0x05,
                      UNIT_ATTENTION    = 0x06,
                      DATA_PROTECT      = 0x07,
                      BLANK_CHECK       = 0x08,
                      VENDOR_SPECIFIC   = 0x09,
                      COPY_ABORTED      = 0x0A,
                      ABORTED_COMMAND   = 0x0B,
                      RESERVED          = 0x0C,
                      VOLUME_OVERFLOW   = 0x0D,
                      MISCOMPARE        = 0x0E,
                      COMPLETED         = 0x0F)

# spc4r30: 4.5.2.1 (page 48)
class SCSISenseDataGenericDescriptor(Struct):
    _fields_ = [
        UBInt8("descriptor_type"),
        VarSizeBuffer("data", UBInt8)
        ]

# spc4r30: 4.5.2.2 (page 49)
class SCSISenseDataDescriptorInformation(Struct):
    _fields_ = [
        ConstField("descriptor_type", 0x00, UBInt8),
        ConstField("additional_length", 0x0A, UBInt8),
        BitFields(
            BitPadding(7),
            BitFlag("valid", default=1),
            ),
        BytePadding(1),
        FixedSizeBuffer("information", 8, default='\x00' * 8)
    ]

SENSE_DESCIPTOR_TYPES = {
    0x00: SCSISenseDataDescriptorInformation,
}

class SCSISenseResponseCode(Struct):
    _fields_ = BitFields(
        BitField("code", 7),
        BitFlag("valid")
    )

# spc4r30: 4.5 (page 45) This is for response_code 72h and 73h
class SCSISenseDataDescriptorBased(Struct):
    _fields_ = [
        Field("response_code", SCSISenseResponseCode),
        BitFields(
            MappingField("sense_key", BitMarshal(4), SCSI_SENSE_KEY),
            BitPadding(4)
            ),
        Field("additional_sense_code", AdditionalSenseCode),
        BytePadding(2),
        SumSizeArray("descriptors", UBInt8,
                     StructSelector(UBInt8, SENSE_DESCIPTOR_TYPES, default=SCSISenseDataGenericDescriptor))
    ]

# spc4r30: 4.5.3 (page 57) This is for response_code 70h and 71h
class SCSISenseDataFixed(Struct):
    _fields_ = [
        Field("response_code", SCSISenseResponseCode),
        BytePadding(1),
        BitFields(
            MappingField("sense_key", BitMarshal(4), SCSI_SENSE_KEY),
            BitPadding(1),
            BitFlag("ili"),
            BitFlag("eom"),
            BitFlag("filemark")
            ),
        UBInt32("information"),
        UBInt8("additional_sense_length"),
        UBInt32("command_specific_information"),
        Field("additional_sense_code", AdditionalSenseCode),
        UBInt8("field_replaceable_unit_code"),
        BitFields(
            BitField("sense_key_specific_high", 7),
            BitFlag("sksv"),
            BitField("sense_key_specific_low", 8)
        )
    ]


def get_sense_object_from_buffer(buf):
    response_code = SCSISenseResponseCode.create_from_string(buf)
    # spc4r30 4.5:
    if response_code.code in (0x70, 0x71):
        sense = SCSISenseDataFixed.create_from_string(buf)
    elif response_code.code in (0x72, 0x73):
        sense = SCSISenseDataDescriptorBased.create_from_string(buf)
    else:
        return None
    return sense
