from .... import SCSIReadCommand
from .. import InquiryCommand

class EVPDInquiryCommand(InquiryCommand):
    def __init__(self, page_code, allocation_length, result_class):
        super(EVPDInquiryCommand, self).__init__(result_class=result_class, page_code=page_code, evpd=1,
                                                 allocation_length=allocation_length)

INQUIRY_PAGE_SUPPORTED_VPD_PAGES = 0x00
INQUIRY_PAGE_UNIT_SERIAL_NUMBER = 0x80
INQUIRY_PAGE_DEVICE_IDENTIFICATION = 0x83

from .unit_serial_number import UnitSerialNumberVPDPageCommand
from .device_identification import DeviceIdentificationVPDPageCommand
from .supported_pages import SupportedVPDPagesCommand

# TODO should we have a default page parser that creates a string of the entire page?

SUPPORTED_VPD_PAGES_COMMANDS = {
    INQUIRY_PAGE_SUPPORTED_VPD_PAGES: SupportedVPDPagesCommand,
    INQUIRY_PAGE_UNIT_SERIAL_NUMBER: UnitSerialNumberVPDPageCommand,
    INQUIRY_PAGE_DEVICE_IDENTIFICATION: DeviceIdentificationVPDPageCommand
}
