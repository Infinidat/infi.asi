from .. import CDB
from ... import SCSIReadCommand
from ..operation_code import OperationCode
from ..control import Control, DEFAULT_CONTROL
from infi.instruct import UBInt8, UBInt16, BitFields, BitPadding, BitField, BitFlag, Struct
from infi.instruct import Field, ConstField
from infi.instruct.buffer import Buffer, be_int_field, bytes_ref
from infi.instruct.buffer.compat import buffer_to_struct_adapter


# spc4r30: 6.4.2 (page 261)
class PeripheralDeviceDataBuffer(Buffer):
    byte_size = 1
    type = be_int_field(where=bytes_ref[0].bits[0:5])  # 0-4
    qualifier = be_int_field(where=bytes_ref[0].bits[5:8])  # 5-7


PeripheralDeviceData = buffer_to_struct_adapter(PeripheralDeviceDataBuffer)


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
        result = self.result_class()
        result.unpack(result_datagram)
        yield result

__all__ = []
