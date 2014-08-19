from .. import PeripheralDeviceDataBuffer
from . import EVPDInquiryCommand
from infi.instruct.buffer import Buffer, str_field, bytes_ref, buffer_field, be_int_field


# sat3r04: 12.4.2
class AtaIdentifyDevice(Buffer):
    byte_size = 512
    # FIXME: The reason for this ugliness is bizare spec definition for these fields.
    # To do it less ugly, we will need additional abilities in instruct module,
    # ability define words as big-endian:
    #    serial_number = str_field(where=bytes_ref[10*2:20*2])  # word 10-19 in ATA IDENTIFY DEVICE range
    #    firmware_revision = str_field(where=bytes_ref[23*2:27*2])  # word 23-26 in ATA IDENTIFY DEVICE range
    #    model_number = str_field(where=bytes_ref[27*2:47*2])  # word 27-46 in ATA IDENTIFY DEVICE range
    serial_number = str_field(where=bytes_ref[21, 20, 23, 22, 25, 24, 27, 26, 29, 28, 31, 30, 33, 32, 35, 34,
                                              37, 36, 39, 38])  # word 10-19 in ATA IDENTIFY DEVICE range
    firmware_revision = str_field(where=bytes_ref[47, 46, 49, 48, 51, 50, 53,
                                                  52])  # word 23-26 in ATA IDENTIFY DEVICE range
    model_number = str_field(where=bytes_ref[55, 54, 57, 56, 59, 58, 61, 60, 63, 62, 65, 64, 67, 66, 69, 68,
                                             71, 70, 73, 72, 75, 74, 77, 76, 79, 78, 81, 80, 83, 82, 85, 84,
                                             87, 86, 89, 88, 91, 90])  # word 27-46 in ATA IDENTIFY DEVICE range


class DeviceSignature(Buffer):
    byte_size = 20
    transport_id = be_int_field(where=bytes_ref[0])
    pm_port = be_int_field(where=bytes_ref[1].bits[0:4])
    interrupt = be_int_field(where=bytes_ref[1].bits[6])
    status = be_int_field(where=bytes_ref[2])
    error = be_int_field(where=bytes_ref[3])
    lba = str_field(where=(bytes_ref[4] + bytes_ref[5] + bytes_ref[6] +
                           bytes_ref[8] + bytes_ref[9] + bytes_ref[10]))
    device = be_int_field(where=bytes_ref[7])
    sector_count = be_int_field(where=bytes_ref[12:14])


class AtaInformationVPDPageBuffer(Buffer):
    byte_size = 572
    peripheral_device = buffer_field(where=bytes_ref[0:], type=PeripheralDeviceDataBuffer)
    page_code = be_int_field(where=bytes_ref[1:2])
    page_length = be_int_field(where=bytes_ref[2:4])
    sat_vendor_identification = str_field(where=bytes_ref[8:16])  # bytes 8-15
    sat_product_identification = str_field(where=bytes_ref[16:32])  # bytes 16-31
    sat_product_revision_level = str_field(where=bytes_ref[32:36])  # bytes 32-35
    device_signature = buffer_field(where=bytes_ref[36:56], type=DeviceSignature)  # bytes 36-55
    command_code = be_int_field(where=bytes_ref[56:57])
    # ATA IDENTIFY DEVICE: bytes 60-571
    identify_device = buffer_field(where=bytes_ref[60:572], type=AtaIdentifyDevice)


# sat3r04: 12.4.2
class AtaInformationVPDPageCommand(EVPDInquiryCommand):
    def __init__(self):
        super(AtaInformationVPDPageCommand, self).__init__(0x89, 1024, AtaInformationVPDPageBuffer)

__all__ = ["AtaInformationVPDPageCommand", "AtaInformationVPDPageBuffer"]
