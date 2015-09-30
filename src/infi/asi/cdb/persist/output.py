from .transport import TransportId
from infi.asi import SCSIWriteCommand
from infi.asi.cdb import CDBBuffer
from infi.asi.cdb.control import DEFAULT_CONTROL_BUFFER, ControlBuffer
from infi.instruct.buffer import *
from infi.instruct.buffer.macros import *

CDB_OPCODE_PERSISTENT_RESERVE_OUT = 0x5F

class PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES(object):
    """
    The various reserve in commands service actions
    See spc-4_rev36: 6.16.2 (P. 386)
    """
    REGISTER = 0x00
    RESERVE = 0x01
    RELEASE = 0x02
    CLEAR = 0x03
    PREEMPT = 0x04
    PREEMPT_AND_ABORT = 0x05
    REGISTER_AND_IGNORE_EXISTING_KEY = 0x06
    REGISTER_AND_MOVE = 0x07
    REPLACE_LOST_RESERVATION = 0x07

class PERSISTENT_RESERVE_OUT_TYPES(object):
    """
    The various reserve types
    See spc-4_rev36: 6.16.2, table 209 (P. 377)
    """
    WRITE_EXCLUSIVE = 0x01
    EXCLUSIVE_ACCESS = 0x03
    WRITE_EXCLUSIVE_REGISTRANTS_ONLY = 0x05
    EXCLUSIVE_ACCESS_REGISTRANTS_ONLY = 0x6
    WRITE_EXCLUSIVE_ALL_REGISTRANTS = 0x07
    EXCLUSIVE_ACCESS_ALL_REGISTRANTS = 0x8

class PersistentReserveOutCommandBasicParameterList(CDBBuffer):
    """
    The buffer class used for generating the basic parameters for the
    persistent reserve out command.
    See spc-4_rev36: 6.16.3 (P. 387)
    """
    reservation_key = be_uint_field(where=bytes_ref[0:8])
    service_action_reservation_key = be_uint_field(where=bytes_ref[8:16])
    activate_persist_through_power_loss = be_uint_field(where=bytes_ref[20].bits[0], set_before_pack=0, default=0)
    obsolete_1 = be_uint_field(where=bytes_ref[16:20], set_before_pack=0, default=0)
    all_target_ports = be_uint_field(where=bytes_ref[20].bits[2], default=0)
    specify_initiator_ports = be_uint_field(where=bytes_ref[20].bits[3], default=0)  
    reserved_1 = be_uint_field(where=bytes_ref[21], set_before_pack=0, default=0)
    obsolete_2 = be_uint_field(where=bytes_ref[22:24], set_before_pack=0, default=0)

class PersistentReserveOutCommandRegisterAndMoveParameterList(CDBBuffer):
    """
    The buffer class used for generating the parameters for the register
    and move service action of thepersistent reserve out command.
    See spc-4_rev36: 6.16.4 (P. 392)
    """
    reservation_key = be_uint_field(where=bytes_ref[0:8])
    service_action_reservation_key = be_uint_field(where=bytes_ref[8:16])
    activate_persist_through_power_loss = be_uint_field(where=bytes_ref[17].bits[0], default=0)
    unregister = be_uint_field(where=bytes_ref[17].bits[1], default=0)
    relative_target_port_identifier = be_uint_field(where=bytes_ref[18:20], default=0)
    transport_id_length = be_uint_field(where=bytes_ref[20:24])
    transport_id = buffer_field(TransportId, where=bytes_ref[24:transport_id_length + 24])

    def __init__(self, transport_id, **kwargs):
        super(PersistentReserveOutCommandRegisterAndMoveParameterList, self).__init__(**kwargs)        
        self.transport_id = transport_id
        self.transport_length = len(transport_id.pack())


class PersistentReserveOutCommand(CDBBuffer):
    """
    The buffer class used for generating the parameters for the register
    and move service action of thepersistent reserve out command.
    See spc-4_rev36: 6.16.4 (P. 392)
    """
    operation_code = be_uint_field(where=bytes_ref[0], set_before_pack=CDB_OPCODE_PERSISTENT_RESERVE_OUT)
    service_action = be_uint_field(where=bytes_ref[1].bits[0:5])
    pr_type = be_uint_field(where=bytes_ref[2].bits[0:4])
    scope = be_uint_field(where=bytes_ref[3].bits[4:8], set_before_pack=0)
    parameter_list_length = be_uint_field(where=bytes_ref[5:9])
    control = buffer_field(type=ControlBuffer, where=bytes_ref[9], set_before_pack=DEFAULT_CONTROL_BUFFER)

    def __init__(self, service_action, reservation_key=0, service_action_reservation_key=0,
                 pr_type=PERSISTENT_RESERVE_OUT_TYPES.WRITE_EXCLUSIVE, **kwargs):
        super(PersistentReserveOutCommand, self).__init__(**kwargs)
        self.service_action = service_action
        self.pr_type = pr_type
        assert self.service_action in SERVICE_ACTION_TO_PARAMETER_LIST_CLASS, \
            "No parameter list class defined for service action %r." % \
            service_action
        parameter_list_buffer_class = \
            SERVICE_ACTION_TO_PARAMETER_LIST_CLASS[service_action]
        parameter_list_buffer = parameter_list_buffer_class(
            reservation_key=reservation_key, service_action_reservation_key=service_action_reservation_key, **kwargs)
        self.parameter_list_datagram = parameter_list_buffer.create_datagram()
        self.parameter_list_length = len(self.parameter_list_datagram)

    def execute(self, executer):
        command_datagram = self.create_datagram()
        result_datagram = yield executer.call(SCSIWriteCommand(
            str(command_datagram), str(self.parameter_list_datagram)))
        yield result_datagram

"""
A mapping between a given service action code and the buffer class used
for generating its parameters.
See spc-4_rev36: 6.16 (P. 384)
"""
SERVICE_ACTION_TO_PARAMETER_LIST_CLASS = {
    PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.REGISTER: PersistentReserveOutCommandBasicParameterList,
    PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.RESERVE: PersistentReserveOutCommandBasicParameterList,
    PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.RELEASE: PersistentReserveOutCommandBasicParameterList,
    PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.CLEAR: PersistentReserveOutCommandBasicParameterList,
    PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.PREEMPT: PersistentReserveOutCommandBasicParameterList,
    PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.PREEMPT_AND_ABORT: PersistentReserveOutCommandBasicParameterList,
    PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.REGISTER_AND_IGNORE_EXISTING_KEY:
        PersistentReserveOutCommandBasicParameterList,
    PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.REGISTER_AND_MOVE:
        PersistentReserveOutCommandRegisterAndMoveParameterList,
    PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.REPLACE_LOST_RESERVATION: PersistentReserveOutCommandBasicParameterList
}