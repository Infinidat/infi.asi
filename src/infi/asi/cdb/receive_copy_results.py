from . import CDB
from .. import SCSIReadCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *
from ..errors import AsiException
# spc4r30: 6.4.1 (page 259)

CDB_OPCODE = 0x84
DEFAULT_BLOCK_SIZE = 512

class RecieveCopyResults(CDB):
    _fields_ = [
        ConstField("opcode", OperationCode(opcode=CDB_OPCODE)),
        BitFields(
            BitPadding(3),
            BitField("service_action", 5),
            ),
        BytePadding(7),
        UBInt32("allocation_length"),
        BytePadding(1),
        Field("control", Control, DEFAULT_CONTROL)
    ]


    def __init__(self, result_class, *args, **kwargs):
        super(RecieveCopyResults, self).__init__(*args, **kwargs)
        self.result_class = result_class

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.allocation_length))
        result = self.result_class.create_from_string(result_datagram)
        yield result

class OperatingParametrsResult(Struct):
        _fields_ = [
        Field("avialable_data", PeripheralDeviceData),
        UBInt8("page_code"),
        UBInt16("page_length"),
        BitFields(BitField("wsnz", 1),
                  BitPadding(7)
                  ),
        UBInt8("maximum_compare_and_write_length"),
        UBInt16("optimal_transfer_length_granularity"),
        UBInt32("maximum_transfer_length"),
        UBInt32("optimal_transfer_length"),
        UBInt32("maximum_prefetch_xdread_xdwrite_transfer_length"),
        UBInt32("maximum_unmap_lba_count"),
        UBInt32("maximum_unmap_block_descriptor_count"),
        UBInt32("optimal_unmap_granularity"),
        BitFields(BitField("unmap_granularity_alignment__high", 7),
                  BitField("ugavalid", 1),
                  BitField("unmap_granularity_alignment__low", 24)
                  ),
        UBInt64("maximum_write_same_length"),
        Padding(21),
    ]
