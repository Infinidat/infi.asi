from .. import CDB
from ... import SCSIReadCommand
from ..operation_code import OperationCode
from ..control import Control, DEFAULT_CONTROL
from infi.instruct import UBInt8, UBInt16, BitFields, BitPadding, BitField, BitFlag, Struct
from infi.instruct import Padding, Field, ConstField
from infi.instruct.errors import InstructError

# spc4r30: 6.4.2 (page 261)
class PeripheralDeviceData(Struct):
    _fields_ = [
        BitFields(
            BitField("type", 5), # 0-4
            BitField("qualifier", 3), # 5-7
        )
    ]

from ..operation_code import CDB_OPCODE_INQUIRY

# spc4r30: 6.4.1 (page 259)
class InquiryCommand(CDB):
    _fields_ = [
        ConstField("opcode", OperationCode(opcode=CDB_OPCODE_INQUIRY)),
        BitFields(
            BitFlag("evpd", default=0),
            BitPadding(7)
        ),
        UBInt8("page_code"),
        UBInt16("allocation_length"),
        Field("control", Control, DEFAULT_CONTROL)
    ]

    def __init__(self, result_class, *args, **kwargs):
        super(InquiryCommand, self).__init__(*args, **kwargs)
        self.result_class = result_class

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.allocation_length))
        result = self.result_class.create_from_string(result_datagram)
        yield result

__all__ = []
