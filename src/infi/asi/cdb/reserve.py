from .control import DEFAULT_CONTROL_BUFFER, ControlBuffer
from . import CDBBuffer
from infi.asi import SCSIWriteCommand
from infi.instruct.buffer import *
from infi.instruct.buffer.macros import *

CDB_OPCODE_RESERVE_6 = 0x16
CDB_OPCODE_RESERVE_10 = 0x56


class Reserve6Command(CDBBuffer):
    """
    The buffer class used for generating the reserve(6) command.
    """
    operation_code = be_uint_field(where=bytes_ref[0], set_before_pack=CDB_OPCODE_RESERVE_6)
    obsolete_1 = be_uint_field(where=bytes_ref[1].bits[0:5], default=0)
    reserved_1 = be_uint_field(where=bytes_ref[1].bits[5:8], default=0)
    obsolete_2 = be_uint_field(where=bytes_ref[2], default=0)
    obsolete_3 = be_uint_field(where=bytes_ref[3:5], default=0)
    control = buffer_field(type=ControlBuffer, where=bytes_ref[5], default=DEFAULT_CONTROL_BUFFER)

    def execute(self, executer):
        command_datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIWriteCommand(bytes(command_datagram), b''))
        yield result_datagram


class Reserve10ParameterList(CDBBuffer):
    """
    The buffer class used for generating the parameters for the reserve(10) command.
    """
    third_party_device_id = be_uint_field(where=bytes_ref[0:8])


class Reserve10Command(CDBBuffer):
    """
    The buffer class used for generating the reserve(10) command.
    """
    operation_code = be_uint_field(where=bytes_ref[0], default=CDB_OPCODE_RESERVE_10)
    obsolete_1 = be_uint_field(where=bytes_ref[1].bits[0], default=0)
    long_id = be_uint_field(where=bytes_ref[1].bits[1], default=0)
    reserved_1 = be_uint_field(where=bytes_ref[1].bits[2:4], default=0)
    third_party = be_uint_field(where=bytes_ref[1].bits[4], default=0)
    reserved_2 = be_uint_field(where=bytes_ref[1].bits[5:8], default=0)
    obsolete_2 = be_uint_field(where=bytes_ref[2], default=0)
    third_party_device_id = be_uint_field(where=bytes_ref[3], default=0)
    reserved_3 = be_uint_field(where=bytes_ref[4:7], default=0)
    parameter_list_length = be_uint_field(where=bytes_ref[7:9], default=0)
    control = buffer_field(type=ControlBuffer, where=bytes_ref[9], default=DEFAULT_CONTROL_BUFFER)

    def __init__(self, third_party_device_id=0, **kwargs):
        super(Reserve10Command, self).__init__(**kwargs)
        self.third_party = 0
        self.parameter_list_datagram = None
        if third_party_device_id > 0:
            self.third_party = 1
            if third_party_device_id < 255:
                self.third_party_device_id = third_party_device_id
                self.long_id = 0
                self.parameter_list_length = 0
            else:
                parameter_list_buffer = Reserve10ParameterList(third_party_device_id=third_party_device_id)
                self.parameter_list_datagram = parameter_list_buffer.create_datagram()
                self.parameter_list_length = 8
                self.long_id = 1

    def execute(self, executer):
        command_datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIWriteCommand(
            bytes(command_datagram),
            bytes(self.parameter_list_datagram) if self.parameter_list_datagram else b''))
        yield result_datagram
