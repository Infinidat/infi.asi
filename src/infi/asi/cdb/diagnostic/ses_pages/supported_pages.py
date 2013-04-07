from infi.instruct.buffer import bytes_ref, be_int_field, uint8, list_field
from . import PCVReceiveDiagnosticResultCommand, DiagnosticDataBuffer


# spc4r36f: 7.2.4
class SupportedDiagnosticPagesData(DiagnosticDataBuffer):
    page_code = be_int_field(where=bytes_ref[0:1])
    page_length = be_int_field(where=bytes_ref[2:4])
    supported_pages = list_field(type=uint8, where=bytes_ref[4:])


# spc4r36f: 7.2.4
class SupportedDiagnosticPagesCommand(PCVReceiveDiagnosticResultCommand):
    def __init__(self):
        super(SupportedDiagnosticPagesCommand, self).__init__(0x00, 255, SupportedDiagnosticPagesData)

__all__ = ["SupportedDiagnosticPagesCommand", "SupportedDiagnosticPagesData"]
