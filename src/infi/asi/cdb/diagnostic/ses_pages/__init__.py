from .. import ReceiveDiagnosticResultCommand
from infi.instruct.buffer import Buffer


class PCVReceiveDiagnosticResultCommand(ReceiveDiagnosticResultCommand):
    def __init__(self, page_code, allocation_length, result_class, conf_page=None):
        super(PCVReceiveDiagnosticResultCommand, self).__init__(result_class=result_class, page_code=page_code, pcv=1,
                                                                allocation_length=allocation_length, conf_page=conf_page)


class DiagnosticDataBuffer(Buffer):
    def __init__(self, conf_page, *args, **kwargs):
        super(DiagnosticDataBuffer, self).__init__(*args, **kwargs)
        self.conf_page = conf_page


DIAGNOSTIC_PAGE_SUPPORTED_PAGES = 0x00
DIAGNOSTIC_PAGE_CONFIGURATION = 0x01
DIAGNOSTIC_PAGE_ENCLOSURE_STATUS = 0x02
DIAGNOSTIC_PAGE_ELEMENT_DESCRIPTOR = 0x07
DIAGNOSTIC_PAGE_VENDOR_0X80 = 0x80


from .supported_pages import SupportedDiagnosticPagesCommand, SupportedDiagnosticPagesData
from .unknown import UnknownDiagnosticPageCommand, UnknownDiagnosticPageData
from .configuration import ConfigurationDiagnosticPagesCommand, ConfigurationDiagnosticPagesData
from .enclosure_status import EnclosureStatusDiagnosticPagesCommand, EnclosureStatusDiagnosticPagesData
from .element_descriptor import ElementDescriptorDiagnosticPagesCommand, ElementDescriptorDiagnosticPagesData
from .vendor_0x80 import Vendor0x80DiagnosticPagesCommand, Vendor0x80DiagnosticPagesData


SUPPORTED_SES_PAGES_COMMANDS = {
    DIAGNOSTIC_PAGE_SUPPORTED_PAGES: SupportedDiagnosticPagesCommand,
    DIAGNOSTIC_PAGE_CONFIGURATION: ConfigurationDiagnosticPagesCommand,
    DIAGNOSTIC_PAGE_ENCLOSURE_STATUS: EnclosureStatusDiagnosticPagesCommand,
    DIAGNOSTIC_PAGE_ELEMENT_DESCRIPTOR: ElementDescriptorDiagnosticPagesCommand,
    DIAGNOSTIC_PAGE_VENDOR_0X80: Vendor0x80DiagnosticPagesCommand
}

SUPPORTED_SES_PAGES_DATA = {
    DIAGNOSTIC_PAGE_SUPPORTED_PAGES: SupportedDiagnosticPagesData,
    DIAGNOSTIC_PAGE_CONFIGURATION: ConfigurationDiagnosticPagesData,
    DIAGNOSTIC_PAGE_ENCLOSURE_STATUS: EnclosureStatusDiagnosticPagesData,
    DIAGNOSTIC_PAGE_ELEMENT_DESCRIPTOR: ElementDescriptorDiagnosticPagesData,
    DIAGNOSTIC_PAGE_VENDOR_0X80: Vendor0x80DiagnosticPagesData
}


def get_ses_page(page_code):
    return SUPPORTED_SES_PAGES_COMMANDS.get(page_code, UnknownDiagnosticPageCommand(page_code))


def get_ses_page_data(page_code):
    return SUPPORTED_SES_PAGES_DATA.get(page_code, UnknownDiagnosticPageData)
