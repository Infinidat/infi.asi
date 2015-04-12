from . import CDB
from .. import SCSIReadCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *

# spc4r30: 6.37 (page 394)

CDB_OPCODE_READCAPACITY_10 = 0x25
CDB_OPCODE_READCAPACITY_16 = 0x9E


class ReadCapacity10Command(CDB):
    _fields_ = [
        ConstField("opcode", OperationCode(opcode=CDB_OPCODE_READCAPACITY_10)),
        Padding(1),
        UBInt32("logical_block_address"),
        Padding(2),
        BitFields(
            BitFlag("pmi", 0),
            BitPadding(7),
            ),
        Field("control", Control, DEFAULT_CONTROL)
    ]

    def __init__(self, logical_block_address=0, pmi=0):
        super(ReadCapacity10Command, self).__init__(logical_block_address=logical_block_address,pmi=pmi)

    def execute(self, executer):
        allocation_length = 8
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, allocation_length))
        result = ReportReadCapacityData10.create_from_string(result_datagram)
        yield result


class ReportReadCapacityData10(Struct):
        _fields_ = [
        UBInt32("last_logical_block_address"),
        UBInt32("block_length_in_bytes"),
        ]


class ReadCapacity16Command(CDB):
    _fields_ = [
        ConstField("opcode", OperationCode(opcode=CDB_OPCODE_READCAPACITY_16)),
        BitFields(
            BitField("service_action", 5, 0x10),
            BitPadding(3),
            ),
        UBInt64("logical_block_address"),
        UBInt32("allocation_length"),
        BitFields(
            BitFlag("pmi", 0),
            BitPadding(7),
            ),
        Field("control", Control, DEFAULT_CONTROL)
    ]

    def __init__(self, logical_block_address=0, pmi=0):
        super(ReadCapacity16Command, self).__init__(logical_block_address=logical_block_address,pmi=pmi)
        self.allocation_length = 32

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.allocation_length))
        result = ReportReadCapacityData16.create_from_string(result_datagram)
        yield result


class ReportReadCapacityData16(Struct):
        _fields_ = [
        UBInt64("last_logical_block_address"),
        UBInt32("block_length_in_bytes"),
        BitFields(
            BitFlag("prot_en", 0),
            BitField("p_type", 3, 0),
            BitPadding(4),
            ),
        BitFields(
            BitField("logical_blocks_per_physical_block", 4, 0),
            BitField("p_i_exponent", 4, 0),
            ),
        BitFields(
            BitField("lowest_aligned_lba_msb", 6, 0),
            BitFlag("troz", 0),
            BitFlag("tpe", 0),
            ),
        UBInt8("lowest_aligned_lba_lsb"),
        Padding(16),
        ]

