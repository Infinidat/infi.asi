from .. import CDB
from ... import SCSIReadCommand
from ..operation_code import OperationCode
from ..control import Control, DEFAULT_CONTROL
from infi.instruct import UBInt8, BitFields, BitPadding, BitField, Flag, Struct
from infi.instruct import Padding, Field, ConstField
from infi.instruct.errors import InstructError

class PeripheralDeviceData(Struct):
    _fields_ = [
        BitFields(
            BitField("type", 5), # 0-4
            BitField("qualifier", 3), # 5-7
        )
    ]

from ..operation_code import CDB_OPCODE_INQUIRY

class InquiryCommand(CDB):
    _fields_ = [
        ConstField("opcode", OperationCode(opcode=CDB_OPCODE_INQUIRY)),
        BitFields(
            Flag("evpd", default=0),
            BitPadding(7)
        ),
        UBInt8("page_code"),
        Padding(1),
        UBInt8("allocation_length"),
        Field("control", Control, DEFAULT_CONTROL)
    ]

__all__ = []
