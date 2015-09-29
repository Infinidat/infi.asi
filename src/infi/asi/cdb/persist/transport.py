from infi.asi.cdb import CDBBuffer
from infi.instruct.buffer import *
from infi.instruct.buffer.macros import *

# spc-4_rev36: 6.15.5
class TransportId(CDBBuffer):
    protocol_identifier = be_uint_field(where=bytes_ref[0].bits[0:4], default=1)
    reserved_1 = be_uint_field(where=bytes_ref[0].bits[4:6], set_before_pack=0)
    format_code = be_uint_field(where=bytes_ref[0].bits[6:8], default=0)
    specific_data = bytearray_field(where=bytes_ref[1:])