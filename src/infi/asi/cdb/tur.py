from . import CDB
from .. import SCSIReadCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *

# spc4r30: 6.37 (page 394)

CDB_OPCODE = 0x00

class TestUnitReadyCommand(CDB):
    _fields_ = [
        ConstField("opcode", OperationCode(opcode=CDB_OPCODE)),
        Padding(4),
        Field("control", Control, DEFAULT_CONTROL)
    ]

    def execute(self, executer):
        datagram = self.create_datagram()
        yield executer.call(SCSIReadCommand(datagram, 0))
        yield True
