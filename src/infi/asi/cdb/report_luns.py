from . import CDB
from .. import SCSIReadCommand
from .operation_code import OperationCode
from .control import Control, DEFAULT_CONTROL
from infi.asi.errors import AsiInternalError
from infi.instruct import *

# spc4r30: 6.37 (page 394)

CDB_OPCODE = 0xA0
ALLOCATION_SIZE_FOR_256_LUNS = 16384


class UnsupportedReportLuns(AsiInternalError):
    pass

class UnsupportedLunAdressing(UnsupportedReportLuns):
    pass

class UnsupportedLogicalUnitAddressingMethod(UnsupportedReportLuns):
    pass


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

        if self.allocation_length >= 16:
            result = ReportLunsData.create_from_string(result_datagram)
            result.normalize_lun_list()
        else:
            len_result_datagram = 0 if not result_datagram else len(result_datagram)
            assert len_result_datagram == self.allocation_length, "did not get the requested buffer"
            result = result_datagram
        yield result

    def __init__(self, select_report=0, allocation_length=16384):
        super(ReportLunsCommand, self).__init__(select_report=select_report,
                                                allocation_length=allocation_length)

class ReportLunsData(Struct):
    _fields_ = [
        UBInt32("lun_list_length"),
        Padding(4),
        SumSizeArray("lun_list", ReadPointer("lun_list_length"), UBInt64),
    ]

    def normalize_lun_list(self):
        for item in self.lun_list:
            if item & 0xFFFFFFFFFFFF: # there is second/third/fourth level addressing
                raise UnsupportedLunAdressing(item)
            if item & 0xC000000000000000: # address method is not 00 (Simple logical unit addressing method)
                raise UnsupportedLogicalUnitAddressingMethod(item)
        self.lun_list = [item >> 48 for item in self.lun_list]
