from infi.instruct.buffer import Buffer, bytes_ref, be_int_field
from . import PCVReceiveDiagnosticResultCommand


class UnknownDiagnosticPageData(Buffer):
    page_code = be_int_field(where=bytes_ref[0:1])
    page_data = be_int_field(where=bytes_ref[1:])


def UnknownDiagnosticPageCommand(page_code):
    class UnknownDiagnosticPageCommand(PCVReceiveDiagnosticResultCommand):
        def __init__(self):
            super(UnknownDiagnosticPageCommand, self).__init__(page_code, 2048, UnknownDiagnosticPageData)
    return UnknownDiagnosticPageCommand

__all__ = ["UnknownDiagnosticPageCommand", "UnknownDiagnosticPageData"]
