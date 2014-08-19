from .. import CDBBuffer
from ... import SCSIReadCommand
from ..control import DEFAULT_CONTROL_BUFFER, ControlBuffer
from infi.instruct.buffer import bytes_ref, be_int_field, buffer_field, be_uint_field
from ..operation_code import CDB_RECEIVE_DIAGNOSTIC_RESULTS


# spc4r36f: 6.28
class ReceiveDiagnosticResultCommand(CDBBuffer):
    opcode = be_int_field(where=bytes_ref[0], set_before_pack=CDB_RECEIVE_DIAGNOSTIC_RESULTS)
    pcv = be_int_field(where=bytes_ref[1].bits[0])
    page_code = be_uint_field(where=bytes_ref[2])
    allocation_length = be_int_field(where=bytes_ref[3:5], sign='unsigned')
    control = buffer_field(type=ControlBuffer, where=bytes_ref[5], set_before_pack=DEFAULT_CONTROL_BUFFER)

    def __init__(self, result_class, conf_page, *args, **kwargs):
        super(ReceiveDiagnosticResultCommand, self).__init__(*args, **kwargs)
        self.result_class = result_class
        self.conf_page = conf_page

    def execute(self, executer):
        datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIReadCommand(str(datagram), self.allocation_length))
        result = self.result_class(conf_page=self.conf_page)
        result.unpack(result_datagram)
        yield result


__all__ = []
