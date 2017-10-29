from .transport import TransportId
from infi.asi.cdb import CDBBuffer
from infi.asi import SCSIReadCommand
from infi.asi.cdb.control import DEFAULT_CONTROL_BUFFER, ControlBuffer
from infi.instruct.buffer import *
# TODO relaative imports

CDB_OPCODE_PERSISTENT_RESERVE_IN = 0x5E

class PERSISTENT_RESERVE_IN_SERVICE_ACTION_CODES(object):
    """
    The various reserve in commands service actions
    See spc-4_rev36: 6.15 (P. 372)
    """
    READ_KEYS = 0x00
    READ_RESERVATION = 0x01
    REPORT_CAPABILITIES = 0x02
    READ_FULL_STATUS = 0x03


class PersistentReserveInReadKeysResponse(CDBBuffer):
    """
    The buffer class for parsing the response of the read keys service
    action of the persistent reserve in command.
    See spc-4_rev36: 6.15.2 (P. 372)
    """
    pr_generation = be_uint_field(where=bytes_ref[0:4])
    additional_length = be_uint_field(where=bytes_ref[4:8])
    key_list = list_field(where=bytes_ref[8:8+additional_length],
                          type=b_uint64,
                          n=additional_length // 8, # divide by number of bytes
                                                   # per key.
                          unpack_if=input_buffer_length >= additional_length + 8)

    def required_allocation_length(self):
        return self.additional_length + 8


class PersistentReserveInReadReservationResponse(CDBBuffer):
    """
    The buffer class for parsing the response of the read reservations
    service action of the persistent reserve in command.
    See spc-4_rev36: 6.15.3 (P. 372)
    """
    pr_generation = be_uint_field(where=bytes_ref[0:4])
    additional_length = be_uint_field(where=bytes_ref[4:8])
    reservation_key = be_uint_field(where=bytes_ref[8:16], unpack_if=input_buffer_length >= 16)
    obsolete_1 = be_uint_field(where=bytes_ref[16:20], unpack_if=input_buffer_length >= 20)
    reserved_1 = be_uint_field(where=bytes_ref[20:21], unpack_if=input_buffer_length >= 21)
    pr_type = be_uint_field(where=bytes_ref[21].bits[0:4], unpack_if=input_buffer_length >= 21)
    scope = be_uint_field(where=bytes_ref[21].bits[4:8], unpack_if=input_buffer_length >= 21)
    obsolete_2 = be_uint_field(where=bytes_ref[22:24], unpack_if=input_buffer_length >= 24)

    def required_allocation_length(self):
        return self.additional_length + 8


class PersistentReserveInReportCapabilitiesResponse(CDBBuffer):
    """
    The buffer class for parsing the response of the report capabilities
    service action of the persistent reserve in command.
    See spc-4_rev36: 6.15.4 (P. 378)
    """
    length = be_uint_field(where=bytes_ref[0:2])
    persist_through_power_lost_capable = be_uint_field(where=bytes_ref[2].bits[0])
    reserved_1 = be_uint_field(where=bytes_ref[2].bits[1])
    all_target_ports_capable = be_uint_field(where=bytes_ref[2].bits[2])
    specify_initiator_ports_capable = be_uint_field(where=bytes_ref[2].bits[3])
    compatible_reservation_handling = be_uint_field(where=bytes_ref[2].bits[4])
    reserved_2 = be_uint_field(where=bytes_ref[2].bits[5:7])
    replace_lost_reservation_capable = be_uint_field(where=bytes_ref[2].bits[7])
    persist_through_power_lost_activates = be_uint_field(where=bytes_ref[3].bits[0])
    reserved_3 = be_uint_field(where=bytes_ref[3].bits[1:4])
    allow_commands = be_uint_field(where=bytes_ref[3].bits[4:7])
    type_mask_valid = be_uint_field(where=bytes_ref[3].bits[7])
    # spc-4_rev36: perssitent reserve type mask, Table 211, page 380
    write_exclusive = be_uint_field(where=bytes_ref[4].bits[1])
    exclusive_access = be_uint_field(where=bytes_ref[4].bits[3])
    write_exclusive_registrants_only = be_uint_field(where=bytes_ref[4].bits[5])
    exclusive_access_registrants_only = be_uint_field(where=bytes_ref[4].bits[6])
    write_exclusive_all_registrants = be_uint_field(where=bytes_ref[4].bits[7])
    exclusive_access_all_registrants = be_uint_field(where=bytes_ref[5].bits[0])
    reserved_4 = be_uint_field(where=bytes_ref[6:8])

    def required_allocation_length(self):
        return 8


class PersistentReserveInReadFullStatusDescriptor(CDBBuffer):
    """
    The buffer class for parsing a single status descriptor of the read
    full status service action of the persistent reserve in command.
    See spc-4_rev36: 6.15.5 (P. 383)
    """
    reservation_key = be_uint_field(where=bytes_ref[0:8])
    reservation_holder = be_uint_field(where=bytes_ref[12].bits[0])
    all_target_ports = be_uint_field(where=bytes_ref[12].bits[1])
    pr_type = be_uint_field(where=bytes_ref[13].bits[0:4])
    scope = be_uint_field(where=bytes_ref[13].bits[4:8])
    relative_target_port_identifier = be_uint_field(where=bytes_ref[18:20])
    additional_length = be_uint_field(where=bytes_ref[20:24])
    transport_id = buffer_field(type=TransportId,
                                where=bytes_ref[24:additional_length + 24])


class PersistentReserveInReadFullStatusResponse(CDBBuffer):
    """
    The buffer class for parsing the response of the read full status
    service action of the persistent reserve in command.
    See spc-4_rev36: 6.15.5 (P. 382)
    """
    pr_generation = be_uint_field(where=bytes_ref[0:4])
    additional_length = be_uint_field(where=bytes_ref[4:8])
    full_status_descriptors = list_field(
        where=bytes_ref[8:8 + additional_length],
        type=PersistentReserveInReadFullStatusDescriptor,
        unpack_if=additional_length > 0)

    def required_allocation_length(self):
        return additional_length + 8


class PersistentReserveInCommand(CDBBuffer):
    """
    The buffer class for generating persisent reserve in commands
    See spc-4_rev36: 6.15 (P. 372)
    """
    operation_code = be_uint_field(where=bytes_ref[0], set_before_pack=CDB_OPCODE_PERSISTENT_RESERVE_IN)
    service_action = be_uint_field(where=bytes_ref[1].bits[0:5])
    allocation_length = be_uint_field(where=bytes_ref[7:9])
    control = buffer_field(type=ControlBuffer, where=bytes_ref[9], set_before_pack=DEFAULT_CONTROL_BUFFER)

    def __init__(self, service_action, allocation_length=520, **kwargs):
        super(PersistentReserveInCommand, self).__init__(
            service_action=service_action,
            allocation_length=allocation_length,
            **kwargs)
        assert allocation_length >= 8, \
            "A minimum of 8 bytes must be allocated."

    def execute(self, executer):
        command_datagram = bytes(self.create_datagram())
        result_datagram = yield executer.call(SCSIReadCommand(command_datagram,
            self.allocation_length))
        assert self.service_action in SERVICE_ACTION_TO_RESPONSE_BUFFER_CLASS, \
            "No unpacking class defined for service action %r." % \
            self.service_action
        result_class = SERVICE_ACTION_TO_RESPONSE_BUFFER_CLASS[self.service_action]
        result = result_class()
        result_class.unpack(result, result_datagram)
        yield result

"""
A mapping between a code of the service actions and the buffer class
used for parsing responses from that action.
"""
SERVICE_ACTION_TO_RESPONSE_BUFFER_CLASS = {
    PERSISTENT_RESERVE_IN_SERVICE_ACTION_CODES.READ_KEYS: PersistentReserveInReadKeysResponse,
    PERSISTENT_RESERVE_IN_SERVICE_ACTION_CODES.READ_RESERVATION: PersistentReserveInReadReservationResponse,
    PERSISTENT_RESERVE_IN_SERVICE_ACTION_CODES.REPORT_CAPABILITIES: PersistentReserveInReportCapabilitiesResponse,
    PERSISTENT_RESERVE_IN_SERVICE_ACTION_CODES.READ_FULL_STATUS: PersistentReserveInReadFullStatusResponse
}
