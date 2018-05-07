from .... import SCSIReadCommand
from .. import InquiryCommand
from collections import defaultdict

class EVPDInquiryCommand(InquiryCommand):
    def __init__(self, page_code, allocation_length, result_class):
        super(EVPDInquiryCommand, self).__init__(result_class=result_class, page_code=page_code, evpd=1,
                                                 allocation_length=allocation_length)


class CustomDefaultDict(defaultdict):

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError((key,))
        self[key] = value = self.default_factory(key)
        return value

INQUIRY_PAGE_SUPPORTED_VPD_PAGES = 0x00
INQUIRY_PAGE_UNIT_SERIAL_NUMBER = 0x80
INQUIRY_PAGE_DEVICE_IDENTIFICATION = 0x83
INQUIRY_PAGE_ATA_INFORMATION = 0x89
INQUIRY_PAGE_BLOCK_LIMITS = 0xb0
INQUIRY_PAGE_LOGICAL_BLOCK_PROVISIONING = 0xb2
INQUIRY_PAGE_VERITAS = 0xc0

from .unit_serial_number import UnitSerialNumberVPDPageCommand, UnitSerialNumberVPDPageBuffer
from .ata_information import AtaInformationVPDPageCommand, AtaInformationVPDPageBuffer
from .device_identification import DeviceIdentificationVPDPageCommand, DeviceIdentificationVPDPageBuffer
from .supported_pages import SupportedVPDPagesCommand, SupportedVPDPagesBuffer
from .block_limits import BlockLimitsPageCommand, BlockLimitsVPDPageBuffer
from .logical_block_provisioning import LogicalBlockProvisioningPageCommand, LogicalBlockProvisioningVPDPageBuffer
from .veritas import VeritasVPDPageCommand, VeritasVPDPageBuffer
from .unknown import UnknownVPDPageCommand, UnknownVPDPageBuffer

# Working Draft SCSI Primary Commands - 4 (SPC-4) - Table 141 (pages 262-263)
SCSI_PERIPHERAL_DEVICE_TYPE = {0x00: "disk",
                               0x01: "tape",
                               0x02: "printer",
                               0x03: "processor",
                               0x04: "write once optical disk",
                               0x05: "cd/dvd",
                               0x06: "scanner",
                               0x07: "optical memory device",
                               0x08: "medium changer",
                               0x09: "communications",
                               0x0a: "graphics [0xa]",
                               0x0b: "graphics [0xb]",
                               0x0c: "storage array controller",
                               0x0d: "enclosure services device",
                               0x0e: "simplified direct access device",
                               0x0f: "optical card reader/writer device",
                               0x10: "bridge controller commands",
                               0x11: "object based storage",
                               0x12: "automation/driver interface",
                               0x13: "security manager device",
                               0x14: "zoned block commands",
                               0x15: "0x15",
                               0x16: "0x16",
                               0x17: "0x17",
                               0x18: "0x18",
                               0x19: "0x19",
                               0x1a: "0x1a",
                               0x1b: "0x1b",
                               0x1c: "0x1c",
                               0x1d: "0x1d",
                               0x1e: "well known logical unit",
                               0x1f: "no physical device on this lu"}

# Working Draft SCSI Primary Commands - 4 (SPC-4) - Table 142 (pages 263)
SCSI_VERSION_NAME = {0x00: "no conformance claimed",
                     0x01: "SCSI-1",
                     0x02: "SCSI-2",
                     0x03: "SPC",
                     0x04: "SPC-2",
                     0x05: "SPC-3",
                     0x06: "SPC-4",
                     0x07: "SPC-5",
                     }

# Working Draft SCSI Primary Commands - 4 (SPC-4) - Table 517 (page 605)
SCSI_VPD_NAME = {0x00: "Supported VPD pages",
                 0x80: "Unit serial number",
                 0x81: "Implemented operating definitions (obsolete)",
                 0x82: "ASCII implemented operating definition (obsolete)",
                 0x83: "Device identification",
                 0x84: "Software interface identification",
                 0x85: "Management network addresses",
                 0x86: "Extended INQUIRY data",
                 0x87: "Mode page policy",
                 0x88: "SCSI ports",
                 0x89: "ATA information",
                 0x8a: "Power condition",
                 0x8b: "Device constituents",
                 0x8c: "CFA profile information",
                 0x8d: "Power consumption",
                 0x8f: "Third party copy",
                 0x90: "Protocol-specific logical unit information",
                 0x91: "Protocol-specific port information",
                 0x92: "SCSI Feature sets",
                 # https://wiki.infinidat.com/display/INFINIBOX10/SCSI+Inquiry+Command#SCSIInquiryCommand-6.INQUIRYPageB0h-BlockLimitsPage
                 0xb0: {0x00: "Block limits (sbc2)",
                        0x01: "Sequential access device capabilities (ssc3)",
                        0x11: "OSD information (osd)"
                        },
                 0xb1: {0x00: "Block device characteristics (sbc3)",
                        0x11: "Security token (osd)",
                        0x0d: "Enclosure services device characteristics (ses4)"
                        },
                 # https://wiki.infinidat.com/display/INFINIBOX10/SCSI+Inquiry+Command#SCSIInquiryCommand-6.1INQUIRYPageB2h-logicalblockprovisioning
                 0xb2: {0x00: "Logical block provisioning (sbc3)",
                        0x01: "TapeAlert supported flags (ssc3)"
                        },
                 0xb3: {0x00: "Referrals (sbc3)"
                        },
                 0xc0: "vendor: Firmware numbers (seagate); Unit path report (EMC)",
                 0xc1: "vendor: Date code (seagate)",
                 0xc2: "vendor: Jumper settings (seagate); Software version (RDAC)",
                 0xc3: "vendor: Device behavior (seagate)",
                 0xc9: "Volume Access Control (RDAC)"
                 }

# Working Draft SCSI Primary Commands - 4 (SPC-4) - Table 23 (page 45)
SCSI_CODE_SETS = {0x01: 'Binary', 0x02: 'ASCII', 0x03: 'UTF8'}

# Working Draft SCSI Primary Commands - 4 (SPC-4) - Table 531 (page 613)
_SCSI_DESIGNATOR_TYPES = {0x00: 'vendor specific [0x0]',
                          0x01: 'T10 vendor identification',
                          0x02: 'EUI-64 based',
                          0x03: 'NAA',
                          0x04: 'Relative target port',
                          0x05: 'Target port group',
                          0x06: 'Logical unit group',
                          0x07: 'MD5 logical unit identifier',
                          0x08: 'SCSI name string',
                          0x09: 'Protocol specific port identifier',
                          0x0a: 'UUID identifier',
                          }

SCSI_DESIGNATOR_TYPES = CustomDefaultDict(lambda i: 'Reserved [%s]' % hex(i), _SCSI_DESIGNATOR_TYPES)

# Working Draft SCSI Primary Commands - 4 (SPC-4) - Table 530 (page 613)
SCSI_DESIGNATOR_ASSOCIATIONS = {0x00: 'Addressed logical unit',
                                0x01: 'Target port',
                                0x02: 'Target device that contains addressed lu',
                                0x03: 'Reserved [0x3]'
                                }


SUPPORTED_VPD_PAGES_COMMANDS = {
    INQUIRY_PAGE_SUPPORTED_VPD_PAGES: SupportedVPDPagesCommand,
    INQUIRY_PAGE_UNIT_SERIAL_NUMBER: UnitSerialNumberVPDPageCommand,
    INQUIRY_PAGE_DEVICE_IDENTIFICATION: DeviceIdentificationVPDPageCommand,
    INQUIRY_PAGE_ATA_INFORMATION: AtaInformationVPDPageCommand,
    INQUIRY_PAGE_BLOCK_LIMITS: BlockLimitsPageCommand,
    INQUIRY_PAGE_LOGICAL_BLOCK_PROVISIONING: LogicalBlockProvisioningPageCommand,
    INQUIRY_PAGE_VERITAS: VeritasVPDPageCommand
}

SUPPORTED_VPD_PAGES_DATA = {
    INQUIRY_PAGE_SUPPORTED_VPD_PAGES: SupportedVPDPagesBuffer,
    INQUIRY_PAGE_UNIT_SERIAL_NUMBER: UnitSerialNumberVPDPageBuffer,
    INQUIRY_PAGE_DEVICE_IDENTIFICATION: DeviceIdentificationVPDPageBuffer,
    INQUIRY_PAGE_ATA_INFORMATION: AtaInformationVPDPageBuffer,
    INQUIRY_PAGE_BLOCK_LIMITS: BlockLimitsVPDPageBuffer,
    INQUIRY_PAGE_LOGICAL_BLOCK_PROVISIONING: LogicalBlockProvisioningVPDPageBuffer,
    INQUIRY_PAGE_VERITAS: VeritasVPDPageBuffer
}


def get_vpd_page(page_code):
    return SUPPORTED_VPD_PAGES_COMMANDS.get(page_code, UnknownVPDPageCommand(page_code))


def get_vpd_page_data(page_code):
    return SUPPORTED_VPD_PAGES_DATA.get(page_code, UnknownVPDPageBuffer)
