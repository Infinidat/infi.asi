from . import CDBBuffer
from .. import SCSIReadCommand
from infi.instruct.buffer import *
from infi.instruct.buffer.macros import *


# spc-4_rev36:415
class ReceiveCopyOperatingParametersCommand(CDBBuffer):
    operation_code = be_uint_field(where=bytes_ref[0], set_before_pack=0x84)
    service_action = be_uint_field(where=bytes_ref[1].bits[0:5], set_before_pack=3)
    allocation_length = be_uint_field(where=bytes_ref[10:14])
    control = be_uint_field(where=bytes_ref[15])

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(bytes(datagram), self.allocation_length))
        result = ReceiveCopyOperatingParametersResponse()
        result.unpack(result_datagram)
        yield result


# spc-4_rev36:416
class ReceiveCopyOperatingParametersResponse(Buffer):
    available_data = be_uint_field(where=bytes_ref[0:4])
    snlid = be_int_field(where=bytes_ref[4].bits[0])
    max_cscd_descriptor_count = be_uint_field(where=bytes_ref[8:10])
    max_segment_descriptor_count = be_uint_field(where=bytes_ref[10:12])
    max_descriptor_list_length = be_uint_field(where=bytes_ref[12:16])
    max_segment_length = be_uint_field(where=bytes_ref[16:20])
    max_inline_data_length = be_uint_field(where=bytes_ref[20:24])
    held_data_limit = be_uint_field(where=bytes_ref[24:28])
    max_stream_device_transfer_size = be_uint_field(where=bytes_ref[28:32])
    total_concurrent_copies = be_uint_field(where=bytes_ref[34:36])
    max_concurrent_copies = be_uint_field(where=bytes_ref[36])
    data_segment_granularity = be_uint_field(where=bytes_ref[37])
    inline_data_granularity = be_uint_field(where=bytes_ref[38])
    held_data_granularity = be_uint_field(where=bytes_ref[39])
    implemented_descriptor_list_length = be_uint_field(where=bytes_ref[43],
                                                       set_before_pack=lambda self: len(self.implemented_descriptor_list))
    implemented_descriptor_list = list_field(type=b_uint8,
                                             where_when_pack=bytes_ref[44:],
                                             where_when_unpack=bytes_ref[44:44 + implemented_descriptor_list_length])
