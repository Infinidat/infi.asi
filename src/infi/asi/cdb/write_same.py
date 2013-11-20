from . import CDB
from .. import SCSIWriteCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *
from ..errors import AsiException
# spc4r30: 6.4.1 (page 259)

CDB_OPCODE_WRITE_SAME_10 = 0x41
CDB_OPCODE_WRITE_SAME_16 = 0x93

# TODO move this
DEFAULT_BLOCK_SIZE = 512


class WriteSame10Command(CDB):
    _fields_ = [
                ConstField("opcode", OperationCode(opcode=CDB_OPCODE_WRITE_SAME_10)),
                BitFields(
                          BitPadding(1),
                          BitFlag("lbdata", 0),
                          BitFlag("pbdata", 0),
                          BitPadding(2),
                          BitField("wrprotect", 3, 0),
                          ),
                UBInt32("logical_block_address"),
                BitFields(
                          BitField("group_number", 5, 0),
                          BitPadding(3)),
                UBInt16("number_of_blocks"),
                Field("control", Control, DEFAULT_CONTROL)
                ]

    def __init__(self, logical_block_address, buffer, number_of_blocks=1 ,block_size=DEFAULT_BLOCK_SIZE):
        super(WriteSame10Command, self).__init__()
        assert (len(buffer) %  DEFAULT_BLOCK_SIZE)==0, "buffer length {0} is not a multiple of {1}".format(len(buffer), DEFAULT_BLOCK_SIZE)
        self.logical_block_address = logical_block_address
        self.buffer = buffer
        self.number_of_blocks = number_of_blocks
        assert self.logical_block_address < 2 ** 32, "lba > 2**32"
        assert self.number_of_blocks < 2 ** 16 , "number_of_blocks > 2**16"

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIWriteCommand(datagram, self.buffer))
        yield result_datagram


class WriteSame16Command(CDB):
    _fields_ = [
                ConstField("opcode", OperationCode(opcode=CDB_OPCODE_WRITE_SAME_16)),
                BitFields(
                          BitPadding(1),
                          BitFlag("lbdata", 0),
                          BitFlag("pbdata", 0),
                          BitFlag("unmap", 0),
                          BitPadding(1),
                          BitField("wrprotect", 3, 0),
                          ),
                UBInt64("logical_block_address"),
                UBInt32("number_of_blocks"),
                BitFields(
                          BitField("group_number", 5, 0),
                          BitPadding(3)),
                Field("control", Control, DEFAULT_CONTROL)
                ]
    def __init__(self, logical_block_address, buffer, number_of_blocks=1 ,block_size=DEFAULT_BLOCK_SIZE):
        super(WriteSame16Command, self).__init__()
        assert (len(buffer) %  DEFAULT_BLOCK_SIZE)==0, "buffer length {0} is not a multiple of {1}".format(len(buffer), DEFAULT_BLOCK_SIZE)
        self.logical_block_address = logical_block_address
        self.buffer = buffer
        self.number_of_blocks = number_of_blocks
        assert self.logical_block_address < 2 ** 64, "lba > 2**64"
        assert self.number_of_blocks < 2 ** 32, "number_of_blocks > 2**32"

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIWriteCommand(datagram, self.buffer))
        yield result_datagram
