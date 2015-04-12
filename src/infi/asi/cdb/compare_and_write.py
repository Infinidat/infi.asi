from . import CDB
from .. import SCSIWriteCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *
from ..errors import AsiException
# spc4r30: 6.4.1 (page 259)

CDB_OPCODE_COMPARE_AND_WRITE = 0x89

# TODO move this
DEFAULT_BLOCK_SIZE = 512


class CompareAndWriteCommand(CDB):
    _fields_ = [
                ConstField("opcode", OperationCode(opcode=CDB_OPCODE_COMPARE_AND_WRITE)),
                BitFields(
                          BitPadding(1),
                          BitFlag("fua_nv", 0),
                          BitPadding(1),
                          BitFlag("fua", 0),
                          BitFlag("dpo", 0),
                          BitField("wrprotect", 3, 0),
                          ),
                UBInt64("logical_block_address"),
                BytePadding(3),
                UBInt8("number_of_logical_blocks"),
                BitFields(
                          BitField("group_number", 5, 0),
                          BitPadding(3)),
                Field("control", Control, DEFAULT_CONTROL)
                ]

    def __init__(self, logical_block_address, buffer, number_of_logical_blocks, block_size=DEFAULT_BLOCK_SIZE):
        super(CompareAndWriteCommand, self).__init__()
        self.logical_block_address = logical_block_address
        self.buffer = buffer
        self.block_size = block_size
        self.number_of_logical_blocks = number_of_logical_blocks
        self.transfer_length = len(buffer) / block_size
        assert len(buffer) % block_size == 0, "buffer length {0} is not a multiple of {1}".format(len(buffer), block_size)

    def execute(self, executer):
        assert self.logical_block_address < 2 ** 64, "lba > 2**64"
        assert self.number_of_logical_blocks < 2 ** 8, "number_of_logical_blocks > 2**8"
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIWriteCommand(datagram, self.buffer))

        yield result_datagram
