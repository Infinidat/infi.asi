from . import CDB
from .. import SCSIWriteCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *
from ..errors import AsiException
# spc4r30: 6.4.1 (page 259)

CDB_OPCODE_WRITESAME_10 = 0x41

# TODO move this
DEFAULT_BLOCK_SIZE = 512


class WriteSame10Command(CDB):
    _fields_ = [
                ConstField("opcode", OperationCode(opcode=CDB_OPCODE_WRITESAME_10)),
                BitFields(
                          BitPadding(1),
                          BitFlag("lbdata", 0),
                          BitFlag("pbdata", 0),
                          BitPadding(2),
                          BitField("wdprotect", 3, 0),
                          ),
                UBInt32("logical_block_address"),
                BitFields(
                          BitField("group_number", 5, 0),
                          BitPadding(3)),
                UBInt16("number_of_blocks"),
                Field("control", Control, DEFAULT_CONTROL)
                ]

    def __init__(self, logical_block_address, block_buffer,number_of_blocks ,block_size=DEFAULT_BLOCK_SIZE):
        super(WriteSame10Command, self).__init__()
        assert len(block_buffer) == DEFAULT_BLOCK_SIZE
        self.logical_block_address = logical_block_address
        self.block_buffer = block_buffer
        self.number_of_blocks = number_of_blocks
        

    def execute(self, executer):
        assert self.logical_block_address < 2 ** 32, "lba > 2**32"
        assert self.number_of_blocks < 2 ** 16 , "number_of_blocks > 2**16"
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIWriteCommand(datagram, self.block_buffer))

        yield result_datagram
