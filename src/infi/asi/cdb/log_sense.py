from infi.asi.cdb import CDBBuffer
from infi.asi import SCSIReadCommand
from infi.asi.cdb.control import ControlBuffer, DEFAULT_CONTROL_BUFFER
from infi.instruct.buffer import *
from infi.instruct.buffer.macros import *


class LogSenseCommand(CDBBuffer):
    operation_code = be_uint_field(where=bytes_ref[0], set_before_pack=0x4d)
    sp = be_uint_field(where=bytes_ref[1].bits[0])
    page_code = be_uint_field(where=bytes_ref[2].bits[0:6])
    pc = be_uint_field(where=bytes_ref[2].bits[6:8])
    subpage_code = be_uint_field(where=bytes_ref[3])
    parameter_pointer = be_uint_field(where=bytes_ref[5:7])
    allocation_length = be_uint_field(where=bytes_ref[7:9])
    control = buffer_field(type=ControlBuffer, where=bytes_ref[9], set_before_pack=DEFAULT_CONTROL_BUFFER)

    def __init__(self, page_code, subpage_code=0, allocation_length=396):
        super(LogSenseCommand, self).__init__()
        self.sp = 0
        self.pc = 0
        self.parameter_pointer = 0
        self.page_code = page_code
        self.subpage_code = subpage_code
        self.allocation_length = allocation_length

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(bytes(datagram), self.allocation_length))
        yield result_datagram
