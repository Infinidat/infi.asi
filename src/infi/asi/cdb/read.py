from . import CDB
from .. import SCSIReadCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *
from ..errors import AsiException
# spc4r30: 6.4.1 (page 259)

CDB_OPCODE_READ_6 = 0x08
CDB_OPCODE_READ_10 = 0x28
CDB_OPCODE_READ_12 = 0xa8
CDB_OPCODE_READ_16 = 0x88

DEFAULT_BLOCK_SIZE = 512

class Read6Command(CDB):
    _fields_ = [
        ConstField("opcode", OperationCode(opcode=CDB_OPCODE_READ_6)),
        BitFields(
            BitField("logical_block_address__msb", 5),
            BitPadding(3),
            ),
        UBInt16("logical_block_address__lsb"),
        UBInt8("transfer_length"),
        Field("control", Control, DEFAULT_CONTROL)
    ]

    def __init__(self, logical_block_address, transfer_length, block_size=DEFAULT_BLOCK_SIZE):
        super(Read6Command, self).__init__()
        self.logical_block_address = logical_block_address
        self.block_size = block_size
        self.transfer_length = transfer_length
        assert self.logical_block_address < 2 ** 21
        assert self.transfer_length < 2 ** 8, "transfer_length should be in range [0,256), instead got: {}".format(self.transfer_length)
        self.logical_block_address__msb = self.logical_block_address >> 16
        self.logical_block_address__lsb = self.logical_block_address & 0xffff

    def execute(self, executer):
        datagram = self.create_datagram()
        read_length = self.block_size * self.transfer_length
        if read_length == 0: # This is only in READ 6
            # read_length = 256 * self.block_size
            read_length = 256 * 512
        result_datagram = yield executer.call(SCSIReadCommand(datagram, read_length))
        yield result_datagram

class Read10Command(CDB):
    _fields_ = [
                ConstField("opcode", OperationCode(opcode=CDB_OPCODE_READ_10)),
                BitFields(
                          BitPadding(1),
                          BitFlag("fua_nv", 0),
                          BitPadding(1),
                          BitFlag("fua", 0),
                          BitFlag("dpo", 0),
                          BitField("rdprotect", 3, 0),
                          ),
                UBInt32("logical_block_address"),
                BitFields(
                          BitField("group_number", 5, 0),
                          BitPadding(3)),
                UBInt16("transfer_length"),
                Field("control", Control, DEFAULT_CONTROL)
                ]

    def __init__(self, logical_block_address, transfer_length, block_size=DEFAULT_BLOCK_SIZE):
        super(Read10Command, self).__init__()
        self.logical_block_address = logical_block_address
        self.block_size = block_size
        self.transfer_length = transfer_length
        assert self.logical_block_address < 2 ** 32
        assert self.transfer_length < 2 ** 16

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.block_size * self.transfer_length))
        yield result_datagram


class Read12Command(CDB):
    _fields_ = [
                ConstField("opcode", OperationCode(opcode=CDB_OPCODE_READ_12)),
                BitFields(
                          BitFlag("RelAdr", 0),
                          BitPadding(2),
                          BitFlag("fua", 0),
                          BitFlag("dpo", 0),
                          BitField("reserved", 3, 0),
                          ),
                UBInt32("logical_block_address"),
                UBInt32("transfer_length"),
                BitFields(
                          BitPadding(8)
                          ),
                Field("control", Control, DEFAULT_CONTROL)
                ]

    def __init__(self, logical_block_address, transfer_length, block_size=DEFAULT_BLOCK_SIZE):
        super(Read12Command, self).__init__()
        self.logical_block_address = logical_block_address
        self.block_size = block_size
        self.transfer_length = transfer_length
        assert self.logical_block_address < 2 ** 32
        assert self.transfer_length < 2 ** 32

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.block_size * self.transfer_length))
        yield result_datagram

class Read16Command(CDB):
    _fields_ = [
                ConstField("opcode", OperationCode(opcode=CDB_OPCODE_READ_16)),
                BitFields(
                          BitPadding(1),
                          BitFlag("fua_nv", 0),
                          BitPadding(1),
                          BitFlag("fua", 0),
                          BitFlag("dpo", 0),
                          BitField("reserved", 3, 0),
                          ),
                UBInt64("logical_block_address"),
                UBInt32("transfer_length"),
                BitFields(
                          BitField("group_number", 5, 0),
                          BitPadding(2),
                          BitFlag("mmc4", 0),
                          ),
                Field("control", Control, DEFAULT_CONTROL)
                ]

    def __init__(self, logical_block_address, transfer_length, block_size=DEFAULT_BLOCK_SIZE):
        super(Read16Command, self).__init__()
        self.logical_block_address = logical_block_address
        self.block_size = block_size
        self.transfer_length = transfer_length
        assert self.logical_block_address < 2 ** 64
        assert self.transfer_length < 2 ** 32

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.block_size * self.transfer_length))
        yield result_datagram
