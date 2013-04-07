from .... import SCSIReadCommand
from .. import InquiryCommand

class EVPDInquiryCommand(InquiryCommand):
    def __init__(self, page_code, allocation_length, result_class):
        super(EVPDInquiryCommand, self).__init__(result_class=result_class, page_code=page_code, evpd=1,
                                                 allocation_length=allocation_length)

INQUIRY_PAGE_SUPPORTED_VPD_PAGES = 0x00
INQUIRY_PAGE_UNIT_SERIAL_NUMBER = 0x80
INQUIRY_PAGE_DEVICE_IDENTIFICATION = 0x83
INQUIRY_PAGE_ATA_INFORMATION = 0x89
INQUIRY_PAGE_BLOCK_LIMITS = 0xb0
INQUIRY_PAGE_VERITAS = 0xc0

from .unit_serial_number import UnitSerialNumberVPDPageCommand, UnitSerialNumberVPDPageData
from .ata_information import AtaInformationVPDPageCommand, AtaInformationVPDPageData
from .device_identification import DeviceIdentificationVPDPageCommand, DeviceIdentificationVPDPageData
from .supported_pages import SupportedVPDPagesCommand, SupportedVPDPagesData
from .block_limits import BlockLimitsPageCommand, BlockLimitsVPDPageData
from .veritas import VeritasVPDPageCommand, VeritasVPDPageData
from .unknown import UnknownVPDPageCommand, UnknownVPDPageData

SUPPORTED_VPD_PAGES_COMMANDS = {
    INQUIRY_PAGE_SUPPORTED_VPD_PAGES: SupportedVPDPagesCommand,
    INQUIRY_PAGE_UNIT_SERIAL_NUMBER: UnitSerialNumberVPDPageCommand,
    INQUIRY_PAGE_DEVICE_IDENTIFICATION: DeviceIdentificationVPDPageCommand,
    INQUIRY_PAGE_ATA_INFORMATION: AtaInformationVPDPageCommand,
    INQUIRY_PAGE_BLOCK_LIMITS: BlockLimitsPageCommand,
    INQUIRY_PAGE_VERITAS: VeritasVPDPageCommand
}

SUPPORTED_VPD_PAGES_DATA = {
    INQUIRY_PAGE_SUPPORTED_VPD_PAGES: SupportedVPDPagesData,
    INQUIRY_PAGE_UNIT_SERIAL_NUMBER: UnitSerialNumberVPDPageData,
    INQUIRY_PAGE_DEVICE_IDENTIFICATION: DeviceIdentificationVPDPageData,
    INQUIRY_PAGE_ATA_INFORMATION: AtaInformationVPDPageData,
    INQUIRY_PAGE_BLOCK_LIMITS: BlockLimitsVPDPageData,
    INQUIRY_PAGE_VERITAS: VeritasVPDPageData
}

def get_vpd_page(page_code):
    return SUPPORTED_VPD_PAGES_COMMANDS.get(page_code, UnknownVPDPageCommand(page_code))

def get_vpd_page_data(page_code):
    return SUPPORTED_VPD_PAGES_DATA.get(page_code, UnknownVPDPageData)
