from . import CDB
from .. import SCSIReadCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *
from ..errors import AsiException
# spc4r30: 6.4.1 (page 259)
from infi.instruct import UBInt32
from cStringIO import StringIO
from infi.instruct.buffer import *


CDB_OPCODE = 0xA3

class TruncationError(AsiException):
    pass

class RTPGCommand(CDB):
    """ report target port groups command
    """
    _fields_ = [
        ConstField("opcode", OperationCode(opcode=CDB_OPCODE)),
        BitFields(
            BitField("service_action", 5, 10),
            BitField("parameter_data_format", 3, 0),
            ),
        Padding(4),
        UBInt32("allocation_length"),
        Padding(1),
        Field("control", Control, DEFAULT_CONTROL)
    ]

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.allocation_length))
        if self.parameter_data_format == 0:
            response = TargetPortGroupLengthOnlyResponse()
            response.unpack(result_datagram)
        elif self.parameter_data_format == 1:
            response=TargetPortGroupExtendedResponse()
            response.unpack(result_datagram)

        yield response

    def __init__(self, parameter_data_format=0, allocation_length=16384):
        super(RTPGCommand, self).__init__(parameter_data_format=parameter_data_format,
                                                allocation_length=allocation_length)
        assert parameter_data_format in (0,1),"wrong parameter_data_format value {}".format(parameter_data_format)

class TargetPortDescriptor(Buffer):
    byte_size = 4
    relative_target_port_identifier = be_uint_field(where=bytes_ref[2:4])

class TargetPortGroupDescriptor(Buffer):
    asymetric_access_state = be_int_field(where=bytes_ref[0].bits[0:4])
    pref = be_int_field(where=bytes_ref[0].bits[7])
    ao_sup = be_int_field(where=bytes_ref[1].bits[0])
    an_sup = be_int_field(where=bytes_ref[1].bits[1])
    s_sup = be_int_field(where=bytes_ref[1].bits[2])
    u_sup = be_int_field(where=bytes_ref[1].bits[3])
    lbd_sup = be_int_field(where=bytes_ref[1].bits[4])
    #ao_sup = be_int_field(where=bytes_ref[1].bits[5])
    o_sup = be_int_field(where=bytes_ref[1].bits[6])
    t_sup = be_int_field(where=bytes_ref[1].bits[7])

    target_port_group = be_uint_field(where=bytes_ref[2:4])

    target_port_count = be_int_field(where=bytes_ref[7])
    target_port_list = list_field(type=TargetPortDescriptor, where=bytes_ref[8:], n=target_port_count)

class TargetPortGroupLengthOnlyResponse(Buffer):
    data_length = be_int_field(where=bytes_ref[0:4])
    descriptor_list = list_field(type=TargetPortGroupDescriptor, where=bytes_ref[4:4 + data_length])

class TargetPortGroupExtendedResponse(Buffer):
    data_length = be_int_field(where=bytes_ref[0:4])
    format_type = be_int_field(where=bytes_ref[4].bits[4:7])
    descriptor_list = list_field(type=TargetPortGroupDescriptor, where=bytes_ref[7:7 + data_length])
    # ...
