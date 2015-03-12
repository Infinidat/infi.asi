from infi.instruct.buffer import (Buffer, be_int_field, be_uint_field, str_field, list_field, bytes_ref, total_size,
                                  bytearray_field, after_ref, member_func_ref, str_type)
from . import PCVReceiveDiagnosticResultCommand, DiagnosticDataBuffer


# ses3r05: 6.1.2
ELEMENT_TYPE_UNSPECIFIED = 0x00
ELEMENT_TYPE_DEVICE_SLOT = 0x01
ELEMENT_TYPE_POWER_SUPPLY = 0x02
ELEMENT_TYPE_COOLING = 0x03
ELEMENT_TYPE_TEMPERATURE_SENSOR = 0x04
ELEMENT_TYPE_DOOR = 0x05
ELEMENT_TYPE_AUDIBLE_ALARM = 0x06
ELEMENT_TYPE_ES_CONTROLLER = 0x07
ELEMENT_TYPE_SCC_CONTROLLER = 0x08
ELEMENT_TYPE_NONVOLATILE_CACHE = 0x09
ELEMENT_TYPE_INVALID_OPERATION_REASON = 0x0A
ELEMENT_TYPE_UNINTERRUPTIBLE_POWER_SUPPLY = 0x0B
ELEMENT_TYPE_DISPLAY = 0x0C
ELEMENT_TYPE_KEYPAD = 0x0D
ELEMENT_TYPE_ENCLOSURE = 0x0E
ELEMENT_TYPE_SCSI_PORT_TRANSCEIVER = 0x0F
ELEMENT_TYPE_LANGUAGE = 0x10
ELEMENT_TYPE_COMMUNICATION_PORT = 0x11
ELEMENT_TYPE_VOLTAGE_SENSOR = 0x12
ELEMENT_TYPE_CURRENT_SENSOR = 0x13
ELEMENT_TYPE_SCSI_TARGET_PORT = 0x14
ELEMENT_TYPE_SCSI_INITIATOR_PORT = 0x15
ELEMENT_TYPE_SUBENCLOSURE = 0x16
ELEMENT_TYPE_ARRAY_DEVICE_SLOT = 0x17
ELEMENT_TYPE_SAS_EXPANDER = 0x18
ELEMENT_TYPE_SAS_CONNECTOR = 0x19
ELEMENT_TYPE_SANMINA_SPECIFIC = 0x9e


ELEMENT_TYPE_CODES = {ELEMENT_TYPE_UNSPECIFIED: 'Unspecified',
                      ELEMENT_TYPE_DEVICE_SLOT: 'Device Slot',
                      ELEMENT_TYPE_POWER_SUPPLY: 'Power Supply',
                      ELEMENT_TYPE_COOLING: 'Cooling',
                      ELEMENT_TYPE_TEMPERATURE_SENSOR: 'Temperature Sensor',
                      ELEMENT_TYPE_DOOR: 'Door',
                      ELEMENT_TYPE_AUDIBLE_ALARM: 'Audible Alarm',
                      ELEMENT_TYPE_ES_CONTROLLER: 'Enclosure Services Controller Electronics',
                      ELEMENT_TYPE_SCC_CONTROLLER: 'SCC Controller Electronics',
                      ELEMENT_TYPE_NONVOLATILE_CACHE: 'Nonvolatile Cache',
                      ELEMENT_TYPE_INVALID_OPERATION_REASON: 'Invalid Operation Reason',
                      ELEMENT_TYPE_UNINTERRUPTIBLE_POWER_SUPPLY: 'Uninterruptible Power Supply',
                      ELEMENT_TYPE_DISPLAY: 'Display',
                      ELEMENT_TYPE_KEYPAD: 'Key Pad Entry',
                      ELEMENT_TYPE_ENCLOSURE: 'Enclosure',
                      ELEMENT_TYPE_SCSI_PORT_TRANSCEIVER: 'SCSI Port/Transceiver',
                      ELEMENT_TYPE_LANGUAGE: 'Language',
                      ELEMENT_TYPE_COMMUNICATION_PORT: 'Communication Port',
                      ELEMENT_TYPE_VOLTAGE_SENSOR: 'Voltage Sensor',
                      ELEMENT_TYPE_CURRENT_SENSOR: 'Current Sensor',
                      ELEMENT_TYPE_SCSI_TARGET_PORT: 'SCSI Target Port',
                      ELEMENT_TYPE_SCSI_INITIATOR_PORT: 'SCSI Initiator Port',
                      ELEMENT_TYPE_SUBENCLOSURE: 'Simple Subenclosure',
                      ELEMENT_TYPE_ARRAY_DEVICE_SLOT: 'Array Device Slot',
                      ELEMENT_TYPE_SAS_EXPANDER: 'SAS Expander',
                      ELEMENT_TYPE_SAS_CONNECTOR: 'SAS Connector',
                      ELEMENT_TYPE_SANMINA_SPECIFIC: 'Sanmina Specific Data'}


class EnclosureDescriptor(Buffer):
    enclosure_services_processes_num = be_int_field(where=bytes_ref[0].bits[0:3])
    relative_enclosure_services_process_identifier = be_int_field(where=bytes_ref[0].bits[4:7])
    subenclosure_identifier = be_int_field(where=bytes_ref[1])
    type_descriptor_headers_num = be_int_field(where=bytes_ref[2])
    enclosure_descriptor_length = be_uint_field(where=bytes_ref[3])
    enclosure_logical_identifier = bytearray_field(where=bytes_ref[4:12])
    enclosure_vendor_identification = str_field(where=bytes_ref[12:20])
    product_identification = str_field(where=bytes_ref[20:36])
    product_revision_level = str_field(where=bytes_ref[36:40])
    vendor_specific_enclosure_information = bytearray_field(where_when_pack=bytes_ref[40:],
                                                            where_when_unpack=bytes_ref[40:enclosure_descriptor_length + 4])


class TypeDescriptorHeader(Buffer):
    element_type = be_int_field(where=bytes_ref[0], sign='unsigned')
    possible_elements_num = be_int_field(where=bytes_ref[1])
    subenclosure_identifier = be_int_field(where=bytes_ref[2])
    type_descriptor_text_length = be_int_field(where=bytes_ref[3])


class ConfigurationDiagnosticPagesData(DiagnosticDataBuffer):
    def _calc_num_type_descriptor_headers(self):
        return sum(desc.type_descriptor_headers_num for desc in self.enclosure_descriptor_list)

    def _unpack_type_descriptor_text(self, buffer, index, **kwargs):
        l = self.type_descriptor_header_list[index].type_descriptor_text_length
        return buffer[0:l].to_bytes(), l

    page_code = be_int_field(where=bytes_ref[0])
    secondary_subenclosures_num = be_int_field(where=bytes_ref[1])
    page_length = be_int_field(where=bytes_ref[2:4], set_before_pack=total_size - 4)
    generation_code = be_int_field(where=bytes_ref[4:8])
    enclosure_descriptor_list = list_field(type=EnclosureDescriptor,
                                           where=bytes_ref[8:],
                                           n=secondary_subenclosures_num + 1)
    type_descriptor_header_list = list_field(where=bytes_ref[after_ref(enclosure_descriptor_list):],
                                             type=TypeDescriptorHeader,
                                             n=member_func_ref(_calc_num_type_descriptor_headers))
    type_descriptor_text_list = list_field(where=bytes_ref[after_ref(type_descriptor_header_list):],
                                           type=str_type,
                                           unpack_selector=_unpack_type_descriptor_text,
                                           n=member_func_ref(_calc_num_type_descriptor_headers))


class ConfigurationDiagnosticPagesCommand(PCVReceiveDiagnosticResultCommand):
    def __init__(self):
        super(ConfigurationDiagnosticPagesCommand, self).__init__(0x01, 65535, ConfigurationDiagnosticPagesData)

__all__ = ["ConfigurationDiagnosticPagesCommand", "ConfigurationDiagnosticPagesData"]
