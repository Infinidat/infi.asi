from infi.instruct.buffer import bytes_ref, be_int_field, uint8, list_field
from . import PCVReceiveDiagnosticResultCommand, DiagnosticDataBuffer


class Vendor0x80DiagnosticPagesData(DiagnosticDataBuffer):
    page_code = be_int_field(where=bytes_ref[0:1])
    page_length = be_int_field(where=bytes_ref[2:4])
    vendor_specific = list_field(type=uint8, where=bytes_ref[4:])


class Vendor0x80DiagnosticPagesCommand(PCVReceiveDiagnosticResultCommand):
    def __init__(self):
        super(Vendor0x80DiagnosticPagesCommand, self).__init__(0x80, 255, Vendor0x80DiagnosticPagesData)

__all__ = ["Vendor0x80DiagnosticPagesCommand", "Vendor0x80DiagnosticPagesData"]
