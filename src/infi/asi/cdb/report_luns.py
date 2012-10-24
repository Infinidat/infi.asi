from . import CDB
from .. import SCSIReadCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.instruct import *

# spc4r30: 6.37 (page 394)

CDB_OPCODE = 0xA0

class ReportLunsCommand(CDB):
    _fields_ = [
        ConstField("opcode", OperationCode(opcode=CDB_OPCODE)),
        Padding(1),
        UBInt8("select_report"),
        Padding(3),
        UBInt32("allocation_length"),
        Padding(1),
        Field("control", Control, DEFAULT_CONTROL)
    ]

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(datagram, self.allocation_length))
        result = ReportLunsPageData.create_from_string(result_datagram)
        yield result

    def __init__(self, select_report=0, allocation_length=252):
        super(ReportLunsCommand, self).__init__(select_report=select_report,
                                                allocation_length=allocation_length)

class ReportLunsPageData(Struct):
	_fields_ = [
        UBInt32("lun_list_length"),
        Padding(4),
        VarSizeArray("lun_list", ReadPointer("lun_list_length"), UBInt64),
	]
