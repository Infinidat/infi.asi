from . import CDB
from .. import SCSIWriteCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *
from ..errors import AsiException
# sbc3r25: 6.4.1 (page 146)

CDB_OPCODE_UNMAP = 0x42

class UnmapCommand(CDB):
    _fields_ = [
                ConstField("opcode", OperationCode(opcode=CDB_OPCODE_UNMAP)),
                Padding(5),
                BitFields(
                          BitField("GROUP_NUMBER", 5,0),
                          BitPadding(3),
                          ),
                UBInt16("parameter_list_length",0),
                Field("control", Control, DEFAULT_CONTROL)
                ]

    def __init__(self, ranges_list=[]):
        super(UnmapCommand, self).__init__()
        blocks=[]
        self.unmap_ubjects=[]
        for range in ranges_list:
            unmap_obj=UnmapParameterListBlock(range[0], range[1])
            self.unmap_ubjects.append(unmap_obj)
            blocks.append(unmap_obj.datagram)
        block_stream = b''.join(blocks)

        self.header_obj=UnmapParameterListHeader(len(block_stream))
        self.buffer=self.header_obj.datagram +block_stream
        self.parameter_list_length=len(self.buffer)

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIWriteCommand(datagram, self.buffer))
        yield result_datagram


class UnmapParameterListHeader(CDB):
    _fields_ = [
                UBInt16("unmap_data_length"),
                UBInt16("unmap_block_descriptor_data_length"),
                Padding(4)
                ]

    def __init__(self, data_length):
        super(UnmapParameterListHeader, self).__init__()
        self.unmap_data_length=data_length+7
        self.unmap_block_descriptor_data_length=data_length
        self.datagram = self.create_datagram()


class UnmapParameterListBlock(CDB):
    _fields_ = [
                UBInt64("unmap_lba"),
                UBInt32("number_of_logical_blocks"),
                Padding(4)
                ]

    def __init__(self, lba, number_of_blocks):
        super(UnmapParameterListBlock, self).__init__()
        self.unmap_lba=lba
        self.number_of_logical_blocks=number_of_blocks
        self.datagram = self.create_datagram()