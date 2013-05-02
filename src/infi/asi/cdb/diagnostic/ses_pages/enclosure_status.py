from infi.instruct.buffer import Buffer, bytes_ref, be_int_field, list_field, buffer_field, int8, member_func_ref
from . import PCVReceiveDiagnosticResultCommand, DiagnosticDataBuffer


class GeneralElementInfo(Buffer):
    byte_size = 3
    general = list_field(type=int8, where=bytes_ref[0:])


# ses3r05: 7.3.2
class DeviceSlotElementInfo(Buffer):
    byte_size = 3
    slot_address = be_int_field(where=bytes_ref[0])
    report = be_int_field(where=bytes_ref[1].bits[0])
    ident = be_int_field(where=bytes_ref[1].bits[1])
    rmv = be_int_field(where=bytes_ref[1].bits[2])
    ready_insert = be_int_field(where=bytes_ref[1].bits[3])
    encl_bypassed_b = be_int_field(where=bytes_ref[1].bits[4])
    encl_bypassed_a = be_int_field(where=bytes_ref[1].bits[5])
    do_not_remove = be_int_field(where=bytes_ref[1].bits[6])
    app_client_bypassed_a = be_int_field(where=bytes_ref[1].bits[7])
    device_bypassed_b = be_int_field(where=bytes_ref[2].bits[0])
    device_bypassed_a = be_int_field(where=bytes_ref[2].bits[1])
    bypassed_b = be_int_field(where=bytes_ref[2].bits[2])
    bypassed_a = be_int_field(where=bytes_ref[2].bits[3])
    device_off = be_int_field(where=bytes_ref[2].bits[4])
    fault_reqstd = be_int_field(where=bytes_ref[2].bits[5])
    fault_sensed = be_int_field(where=bytes_ref[2].bits[6])
    app_client_bypassed_b = be_int_field(where=bytes_ref[2].bits[7])


# ses3r05: 7.3.3
class ArrayDeviceSlotElementInfo(Buffer):
    byte_size = 3
    rr_abort = be_int_field(where=bytes_ref[0].bits[0])
    rebuild_remap = be_int_field(where=bytes_ref[0].bits[1])
    in_failed_array = be_int_field(where=bytes_ref[0].bits[2])
    in_crit_array = be_int_field(where=bytes_ref[0].bits[3])
    cons_chk = be_int_field(where=bytes_ref[0].bits[4])
    hot_spare = be_int_field(where=bytes_ref[0].bits[5])
    rsvd_device = be_int_field(where=bytes_ref[0].bits[6])
    ok = be_int_field(where=bytes_ref[0].bits[7])
    report = be_int_field(where=bytes_ref[1].bits[0])
    ident = be_int_field(where=bytes_ref[1].bits[1])
    rmv = be_int_field(where=bytes_ref[1].bits[2])
    ready_insert = be_int_field(where=bytes_ref[1].bits[3])
    encl_bypassed_b = be_int_field(where=bytes_ref[1].bits[4])
    encl_bypassed_a = be_int_field(where=bytes_ref[1].bits[5])
    do_not_remove = be_int_field(where=bytes_ref[1].bits[6])
    app_client_bypassed_a = be_int_field(where=bytes_ref[1].bits[7])
    device_bypassed_b = be_int_field(where=bytes_ref[2].bits[0])
    device_bypassed_a = be_int_field(where=bytes_ref[2].bits[1])
    bypassed_b = be_int_field(where=bytes_ref[2].bits[2])
    bypassed_a = be_int_field(where=bytes_ref[2].bits[3])
    device_off = be_int_field(where=bytes_ref[2].bits[4])
    fault_reqstd = be_int_field(where=bytes_ref[2].bits[5])
    fault_sensed = be_int_field(where=bytes_ref[2].bits[6])
    app_client_bypassed_b = be_int_field(where=bytes_ref[2].bits[7])


# ses3r05: 7.3.4
class PowerSupplyElementInfo(Buffer):
    byte_size = 3
    ident = be_int_field(where=bytes_ref[0].bits[7])
    dc_over_current = be_int_field(where=bytes_ref[1].bits[1])
    dc_under_voltage = be_int_field(where=bytes_ref[1].bits[2])
    dc_over_voltage = be_int_field(where=bytes_ref[1].bits[3])
    dc_fail = be_int_field(where=bytes_ref[2].bits[0])
    ac_fail = be_int_field(where=bytes_ref[2].bits[1])
    temp_warn = be_int_field(where=bytes_ref[2].bits[2])
    overtmp_fail = be_int_field(where=bytes_ref[2].bits[3])
    off = be_int_field(where=bytes_ref[2].bits[4])
    reqstd_on = be_int_field(where=bytes_ref[2].bits[5])
    fail = be_int_field(where=bytes_ref[2].bits[6])
    hot_swap = be_int_field(where=bytes_ref[2].bits[7])


# ses3r05: 7.3.5
FAN_SPEED_CODE = {0: 'Cooling mechanism is stopped',
                  1: 'Cooling mechanism is at its lowest speed',
                  2: 'Cooling mechanism is at its second lowest speed',
                  3: 'Cooling mechanism is at its third lowest speed',
                  4: 'Cooling mechanism is at its intermediate speed',
                  5: 'Cooling mechanism is at its third highest speed',
                  6: 'Cooling mechanism is at its second highest speed',
                  7: 'Cooling mechanism is at its highest speed'}


class CoolingElementInfo(Buffer):
    byte_size = 3
    # for real fan speed the fan speed value should be multiplied by a factor of 10
    fan_speed = be_int_field(where=(bytes_ref[0].bits[0:3] + bytes_ref[1]))
    ident = be_int_field(where=bytes_ref[0].bits[7])
    speed_code = be_int_field(where=bytes_ref[2].bits[0:3])
    off = be_int_field(where=bytes_ref[2].bits[4])
    reqstd_on = be_int_field(where=bytes_ref[2].bits[5])
    fail = be_int_field(where=bytes_ref[2].bits[6])
    hot_swap = be_int_field(where=bytes_ref[2].bits[7])


# ses3r05: 7.3.6
class TempSensorElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    temperature = be_int_field(where=bytes_ref[1])
    ut_warn = be_int_field(where=bytes_ref[2].bits[0])
    ut_fail = be_int_field(where=bytes_ref[2].bits[1])
    ot_warn = be_int_field(where=bytes_ref[2].bits[2])
    ot_fail = be_int_field(where=bytes_ref[2].bits[3])


# ses3r05: 7.3.7
class DoorElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    unlocked = be_int_field(where=bytes_ref[2].bits[0])
    door_open = be_int_field(where=bytes_ref[2].bits[1])


# ses3r05: 7.3.8
class AudibleAlarmElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    tui_unrecov = be_int_field(where=bytes_ref[2].bits[0])
    tui_crit = be_int_field(where=bytes_ref[2].bits[1])
    tui_non_crit = be_int_field(where=bytes_ref[2].bits[2])
    tui_info = be_int_field(where=bytes_ref[2].bits[3])
    remind = be_int_field(where=bytes_ref[2].bits[4])
    muted = be_int_field(where=bytes_ref[2].bits[6])
    rqst_mute = be_int_field(where=bytes_ref[2].bits[7])


# ses3r05: 7.3.9
class EnclosureServiceControllerElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    report = be_int_field(where=bytes_ref[1].bits[0])
    hot_swap = be_int_field(where=bytes_ref[2].bits[7])


# ses3r05: 7.3.10
class SccControllerElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    report = be_int_field(where=bytes_ref[1].bits[0])


# ses3r05: 7.3.11
class NonVolotileCacheElementInfo(Buffer):
    byte_size = 3
    size_mult = be_int_field(where=bytes_ref[0].bits[0:2])
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    cache_size = be_int_field(where=bytes_ref[1:])


# ses3r05: 7.3.12
class InvalidOpReasonElementInfo(Buffer):
    byte_size = 3
    invop_type = be_int_field(where=bytes_ref[0].bits[6:8])
    invop_bytes = be_int_field(where=bytes_ref[1:])


# ses3r05: 7.3.13
class UninterruptiblePowerSupplyElementInfo(Buffer):
    byte_size = 3
    battery_status = be_int_field(where=bytes_ref[0])
    intf_fail = be_int_field(where=bytes_ref[1].bits[0])
    warn = be_int_field(where=bytes_ref[1].bits[1])
    ups_fail = be_int_field(where=bytes_ref[1].bits[2])
    dc_fail = be_int_field(where=bytes_ref[1].bits[3])
    ac_fail = be_int_field(where=bytes_ref[1].bits[4])
    ac_qual = be_int_field(where=bytes_ref[1].bits[5])
    ac_hi = be_int_field(where=bytes_ref[1].bits[6])
    ac_low = be_int_field(where=bytes_ref[1].bits[7])
    bpf = be_int_field(where=bytes_ref[2].bits[0])
    batt_fail = be_int_field(where=bytes_ref[2].bits[1])
    fail = be_int_field(where=bytes_ref[2].bits[6])
    ident = be_int_field(where=bytes_ref[2].bits[7])


# ses3r05: 7.3.14
class DisplayElementInfo(Buffer):
    byte_size = 3
    display_mode_status = be_int_field(where=bytes_ref[0].bits[0:2])
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    display_char_status = be_int_field(where=bytes_ref[1:])


# ses3r05: 7.3.15
class KeypadElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])


# ses3r05: 7.3.16
class EnclosureElementInfo(Buffer):
    byte_size = 3
    ident = be_int_field(where=bytes_ref[0].bits[7])
    warn_indication = be_int_field(where=bytes_ref[1].bits[0])
    failure_indication = be_int_field(where=bytes_ref[1].bits[1])
    time_until_power_cycle = be_int_field(where=bytes_ref[1].bits[2:8])
    warn_requested = be_int_field(where=bytes_ref[1].bits[0])
    failure_requested = be_int_field(where=bytes_ref[1].bits[1])
    requested_power_off_duration = be_int_field(where=bytes_ref[1].bits[2:8])


# ses3r05: 7.3.17
class ScsiPortTransceiverElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    report = be_int_field(where=bytes_ref[1].bits[0])
    xmit_fail = be_int_field(where=bytes_ref[2].bits[0])
    lol = be_int_field(where=bytes_ref[2].bits[1])
    disabled = be_int_field(where=bytes_ref[2].bits[4])


# ses3r05: 7.3.18
class LanguageElementInfo(Buffer):
    byte_size = 3
    ident = be_int_field(where=bytes_ref[0].bits[7])
    language_code = be_int_field(where=bytes_ref[1:])


# ses3r05: 7.3.19
class CommunicationPortElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    disabled = be_int_field(where=bytes_ref[2].bits[0])


# ses3r05: 7.3.20
class VoltageSensorElementInfo(Buffer):
    byte_size = 3
    crit_under = be_int_field(where=bytes_ref[0].bits[0])
    crit_over = be_int_field(where=bytes_ref[0].bits[1])
    warn_under = be_int_field(where=bytes_ref[0].bits[2])
    warn_over = be_int_field(where=bytes_ref[0].bits[3])
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    voltage = be_int_field(where=bytes_ref[1:])


# ses3r05: 7.3.21
class CurrentSensorElementInfo(Buffer):
    byte_size = 3
    crit_over = be_int_field(where=bytes_ref[0].bits[1])
    warn_over = be_int_field(where=bytes_ref[0].bits[3])
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    current = be_int_field(where=bytes_ref[1:])


# ses3r05: 7.3.22
class ScsiTargetPortElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    report = be_int_field(where=bytes_ref[1].bits[0])
    enabled = be_int_field(where=bytes_ref[2].bits[0])


# ses3r05: 7.3.23
class ScsiInitiatorPortElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    report = be_int_field(where=bytes_ref[1].bits[0])
    enabled = be_int_field(where=bytes_ref[2].bits[0])


# ses3r05: 7.3.24
class SimpleSubenclosureElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    short_enclosure_status = be_int_field(where=bytes_ref[2])


# ses3r05: 7.3.25
class SasExpanderElementInfo(Buffer):
    byte_size = 3
    fail = be_int_field(where=bytes_ref[0].bits[6])
    ident = be_int_field(where=bytes_ref[0].bits[7])


# ses3r05: 7.3.26
class SasConnectorElementInfo(Buffer):
    byte_size = 3
    connector_type = be_int_field(where=bytes_ref[0].bits[0:7])
    ident = be_int_field(where=bytes_ref[0].bits[7])
    connector_phys_link = be_int_field(where=bytes_ref[1])
    fail = be_int_field(where=bytes_ref[2].bits[6])


# ses3r05: 7.2.3
ELEMENT_STATUS_CODE = {0x00: 'Unsupported',
                       0x01: 'OK',
                       0x02: 'Critical',
                       0x03: 'Noncritical',
                       0x04: 'Unrecoverable',
                       0x05: 'Not Installed',
                       0x06: 'Unknown',
                       0x07: 'Not Available',
                       0x08: 'No Access'}


class BaseStatusElement(Buffer):
    byte_size = 4
    element_status_code = be_int_field(where=bytes_ref[0].bits[0:4])
    swap = be_int_field(where=bytes_ref[0].bits[4])
    disabled = be_int_field(where=bytes_ref[0].bits[5])
    prdfail = be_int_field(where=bytes_ref[0].bits[6])


class GeneralStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=GeneralElementInfo)

VendorSpecificElement = GeneralStatusElement


class DeviceSlotStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=DeviceSlotElementInfo)


class ArrayDeviceSlotStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=ArrayDeviceSlotElementInfo)


class PowerSupplyStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=PowerSupplyElementInfo)


class CoolingStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=CoolingElementInfo)


class TempSensorStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=TempSensorElementInfo)


class DoorElementStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=DoorElementInfo)


class AudibleAlarmStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=AudibleAlarmElementInfo)


class EnclosureServiceControllerStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=EnclosureServiceControllerElementInfo)


class SccControllerStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=SccControllerElementInfo)


class UninterruptiblePowerSupplyStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=UninterruptiblePowerSupplyElementInfo)


class InvalidOpReasonStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=InvalidOpReasonElementInfo)


class NonVolotileCacheStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=NonVolotileCacheElementInfo)


class DisplayStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=DisplayElementInfo)


class KeypadStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=KeypadElementInfo)


class EnclosureStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=EnclosureElementInfo)


class ScsiPortTransceiverStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=ScsiPortTransceiverElementInfo)


class LanguageStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=LanguageElementInfo)


class CommunicationPortStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=CommunicationPortElementInfo)


class VoltageSensorStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=VoltageSensorElementInfo)


class CurrentSensorStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=CurrentSensorElementInfo)


class ScsiTargetPortStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=ScsiTargetPortElementInfo)


class ScsiInitiatorPortStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=ScsiInitiatorPortElementInfo)


class SimpleSubenclosureStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=SimpleSubenclosureElementInfo)


class SasExpanderStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=SasExpanderElementInfo)


class SasConnectorStatusElement(BaseStatusElement):
    status_info = buffer_field(where=bytes_ref[1:4], type=SasConnectorElementInfo)


ELEMENT_TYPE_TO_ELEMENT_INFO = {0x00: GeneralStatusElement,
                                0x01: DeviceSlotStatusElement,
                                0x02: PowerSupplyStatusElement,
                                0x03: CoolingStatusElement,
                                0x04: TempSensorStatusElement,
                                0x05: DoorElementStatusElement,
                                0x06: AudibleAlarmStatusElement,
                                0x07: EnclosureServiceControllerStatusElement,
                                0x08: SccControllerStatusElement,
                                0x09: NonVolotileCacheStatusElement,
                                0x0A: InvalidOpReasonStatusElement,
                                0x0B: UninterruptiblePowerSupplyStatusElement,
                                0x0C: DisplayStatusElement,
                                0x0D: KeypadStatusElement,
                                0x0E: EnclosureStatusElement,
                                0x0F: ScsiPortTransceiverStatusElement,
                                0x10: LanguageStatusElement,
                                0x11: CommunicationPortStatusElement,
                                0x12: VoltageSensorStatusElement,
                                0x13: CurrentSensorStatusElement,
                                0x14: ScsiTargetPortStatusElement,
                                0x15: ScsiInitiatorPortStatusElement,
                                0x16: SimpleSubenclosureStatusElement,
                                0x17: ArrayDeviceSlotStatusElement,
                                0x18: SasExpanderStatusElement,
                                0x19: SasConnectorStatusElement,
                                0x9e: VendorSpecificElement}


class StatusDescriptor(Buffer):
    def _unpack_status_element(self, buffer, index, **kwargs):
        elem_type = self.type_descriptor_header.element_type
        if elem_type in ELEMENT_TYPE_TO_ELEMENT_INFO:
            return ELEMENT_TYPE_TO_ELEMENT_INFO[elem_type]
        else:
            return GeneralStatusElement

    def _possible_elements_num(self):
        return self.type_descriptor_header.possible_elements_num

    overall_element = buffer_field(where=bytes_ref[0:4], type=GeneralStatusElement)
    individual_elements = list_field(where=bytes_ref[4:], type=GeneralStatusElement,
                                     unpack_selector=_unpack_status_element,
                                     n=member_func_ref(_possible_elements_num))

    def unpack(self, buffer, type_descriptor_header):
        self.type_descriptor_header = type_descriptor_header
        return super(StatusDescriptor, self).unpack(buffer)


# ses3r05: 6.1.4
class EnclosureStatusDiagnosticPagesData(DiagnosticDataBuffer):
    def _unpack_status_descriptor(self, buffer, index, **kwargs):
        descriptor = StatusDescriptor()
        bytes = descriptor.unpack(buffer, self.conf_page.type_descriptor_header_list[index])
        return descriptor, bytes

    def _possible_elements_num(self):
        return len(self.conf_page.type_descriptor_header_list)

    page_code = be_int_field(where=bytes_ref[0])
    unrecov = be_int_field(where=bytes_ref[1].bits[0])
    crit = be_int_field(where=bytes_ref[1].bits[1])
    non_crit = be_int_field(where=bytes_ref[1].bits[2])
    info = be_int_field(where=bytes_ref[1].bits[3])
    invop = be_int_field(where=bytes_ref[1].bits[4])
    page_length = be_int_field(where=bytes_ref[2:4])
    generation_code = be_int_field(where=bytes_ref[4:8])
    status_descriptors = list_field(where=bytes_ref[8:], type=StatusDescriptor,
                                    unpack_selector=_unpack_status_descriptor,
                                    n=member_func_ref(_possible_elements_num))


class EnclosureStatusDiagnosticPagesCommand(PCVReceiveDiagnosticResultCommand):
    def __init__(self, conf_page):
        super(EnclosureStatusDiagnosticPagesCommand, self).__init__(0x02, 65535, EnclosureStatusDiagnosticPagesData, conf_page)

__all__ = ["EnclosureStatusDiagnosticPagesCommand", "EnclosureStatusDiagnosticPagesData"]
