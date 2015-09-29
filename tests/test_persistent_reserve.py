from infi.unittest import TestCase

PRI_READ_RESERVATIONS_RESPONSE_SAMPLE = \
    (b"\x00\x00\x00\x37\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\xab\xba" +
     b"\x00\x00\x00\x00\x00\x01\x00\x00")

PRO_READ_RESERVATIONS_BASIC_PARAMETERS_SAMPLE = \
    (b"\x00\x00\x00\x00\x00\x00\x0a\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")

PRO_READ_RESERVATIONS_REGISTER_AND_MOVE_PARAMETERS_SAMPLE = \
    (b"\x00\x00\x00\x00\x00\x00\x0a\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x07\x00\x00\x00\x08\x01\x01\x02" + \
     b"\x03\x04\x05\x06\x07")

class TestPersistentReserveIn(TestCase):
    def test_generate_command(self):
        """
        Operation code (0x5e)
        Service action: Read Reservation (0x01)
        Allocation length (0x20)
        """
        from infi.asi.cdb.persist.input import PersistentReserveInCommand, PERSISTENT_RESERVE_IN_SERVICE_ACTION_CODES
        obj = PersistentReserveInCommand(service_action=PERSISTENT_RESERVE_IN_SERVICE_ACTION_CODES.READ_RESERVATION,
                                         allocation_length=0x2000)
        self.assertEquals(obj.pack(), b"\x5e\x01\x00\x00\x00\x00\x00\x20\x00\x00")

    def test_parse_read_keys(self):
        """
        Operation code (0x5e)
        Service action: Read Reservation (0x01)
        Allocation length (0x20)
        """
        from infi.asi.cdb.persist.input import PersistentReserveInReadKeysResponse
        obj = PersistentReserveInReadKeysResponse()
        cmd = b"\x00\x00\x00\x35\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\xab\xba"
        PersistentReserveInReadKeysResponse.unpack(obj, cmd)
        self.assertEquals(obj.pr_generation, 0x00000035)
        self.assertEquals(obj.key_list, [0xABBA])
        self.assertEquals(16, obj.required_allocation_length())
        poor_allocating_command = PersistentReserveInReadKeysResponse() 
        PersistentReserveInReadKeysResponse.unpack(poor_allocating_command,
            b"\x00\x00\x00\x35\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\xab\xba")
        self.assertEquals(16, poor_allocating_command.required_allocation_length())


    def test_parse_read_reservations(self):
        """
        Operation code (0x5e)
        Service action: Read Reservation (0x01)
        Allocation length (0x20)
        """
        from infi.asi.cdb.persist.input import PersistentReserveInReadReservationResponse
        obj = PersistentReserveInReadReservationResponse()
        PersistentReserveInReadReservationResponse.unpack(obj, PRI_READ_RESERVATIONS_RESPONSE_SAMPLE)
        self.assertEquals(obj.pr_generation, 0x00000037)
        self.assertEquals(obj.reservation_key, 0xABBA)
        self.assertEquals(obj.pr_type, 1)
        self.assertEquals(obj.scope, 0)
        self.assertEquals(obj.reservation_key, 0xABBA)
        self.assertEquals(24, obj.required_allocation_length())
        poor_allocating_command = PersistentReserveInReadReservationResponse()
        PersistentReserveInReadReservationResponse.unpack(poor_allocating_command,
            PRI_READ_RESERVATIONS_RESPONSE_SAMPLE)
        self.assertEquals(24, poor_allocating_command.required_allocation_length())

    def test_parse_report_capabilities_of_infinibox_machine(self):
        """
        Operation code (0x5e)
        Service action: Read Reservation (0x01)
        Allocation length (0x20)
        """
        from infi.asi.cdb.persist.input import PersistentReserveInReportCapabilitesResponse
        obj = PersistentReserveInReportCapabilitesResponse()
        PersistentReserveInReportCapabilitesResponse.unpack(obj, b"\x00\x08\x10\x00\x00\x00\x00\x00")
        self.assertEquals(obj.length, 0x0008)
        self.assertEquals(obj.persist_through_power_lost_capable, 0)
        self.assertEquals(obj.reserved_1, 0)
        self.assertEquals(obj.all_target_ports_capable, 0)
        self.assertEquals(obj.specify_initiator_ports_capable, 0)
        self.assertEquals(obj.compatible_reservation_handling, 1)
        self.assertEquals(obj.reserved_2, 0)
        self.assertEquals(obj.replace_lost_reservation_capable, 0)
        self.assertEquals(obj.persist_through_power_lost_activates, 0)
        self.assertEquals(obj.reserved_3, 0)
        self.assertEquals(obj.allow_commands, 0)
        self.assertEquals(obj.type_mask_valid, 0)
        self.assertEquals(obj.write_exclusive, 0)
        self.assertEquals(obj.exclusive_acccess, 0)
        self.assertEquals(obj.write_exclusive_registrants_only, 0)
        self.assertEquals(obj.exclusive_acccess_registrants_only, 0)
        self.assertEquals(obj.write_exclusive_all_registrants, 0)
        self.assertEquals(obj.exclusive_acccess_all_registrants, 0)
        self.assertEquals(obj.reserved_4, 0)

    def test_parse_report_capabilities_of_highly_capable_machine(self):
        """
        Operation code (0x5e)
        Service action: Read Reservation (0x01)
        Allocation length (0x20)
        """
        from infi.asi.cdb.persist.input import PersistentReserveInReportCapabilitesResponse
        obj = PersistentReserveInReportCapabilitesResponse()
        PersistentReserveInReportCapabilitesResponse.unpack(obj, b"\x00\x08\x89\xF1\xA2\x01\x00\x00")
        self.assertEquals(obj.length, 0x0008)
        self.assertEquals(obj.persist_through_power_lost_capable, 1)
        self.assertEquals(obj.reserved_1, 0)
        self.assertEquals(obj.all_target_ports_capable, 0)
        self.assertEquals(obj.specify_initiator_ports_capable, 1)
        self.assertEquals(obj.compatible_reservation_handling, 0)
        self.assertEquals(obj.reserved_2, 0)
        self.assertEquals(obj.replace_lost_reservation_capable, 1)
        self.assertEquals(obj.persist_through_power_lost_activates, 1)
        self.assertEquals(obj.reserved_3, 0)
        self.assertEquals(obj.allow_commands, 0x7)
        self.assertEquals(obj.type_mask_valid, 1)
        self.assertEquals(obj.write_exclusive, 1)
        self.assertEquals(obj.exclusive_acccess, 0)
        self.assertEquals(obj.write_exclusive_registrants_only, 1)
        self.assertEquals(obj.exclusive_acccess_registrants_only, 0)
        self.assertEquals(obj.write_exclusive_all_registrants, 1)
        self.assertEquals(obj.exclusive_acccess_all_registrants, 1)
        self.assertEquals(obj.reserved_4, 0)

class TestPersistentReserveOut(TestCase):
    def test_generate_command(self):
        """
        Operation code (0x5e)
        Service action: Read Reservation (0x01)
        Allocation length (0x20)
        """
        from infi.asi.cdb.persist.output import PersistentReserveOutCommand, PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES
        obj = PersistentReserveOutCommand(service_action=PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.RESERVE)
        self.assertEquals(obj.pack(), b"\x5f\x01\x01\x00\x00\x00\x00\x00\x18\x00")  

    def test_generate_parameter_list_basic(self):
        """
        Operation code (0x5e)
        Service action: Read Reservation (0x01)
        Allocation length (0x20)
        """
        from infi.asi.cdb.persist.output import PersistentReserveOutCommandBasicParameterList
        obj = PersistentReserveOutCommandBasicParameterList(reservation_key=0xabb, service_action_reservation_key=0)
        self.assertEquals(obj.pack(), PRO_READ_RESERVATIONS_BASIC_PARAMETERS_SAMPLE)

    def test_generate_parameter_list_register_and_move(self):
        """
        Operation code (0x5e)
        Service action: Read Reservation (0x01)
        Allocation length (0x20)
        """
        from infi.asi.cdb.persist.transport import TransportId
        from infi.asi.cdb.persist.output import PersistentReserveOutCommandRegisterAndMoveParameterList
        transport_id = TransportId(format_code=0,
                                   protocol_identifier=1,
                                   specific_data=[1,2,3,4,5,6,7])
        transport_id_length = len(transport_id.pack())
        obj = PersistentReserveOutCommandRegisterAndMoveParameterList(reservation_key=0xabb,
                                                                      service_action_reservation_key=0,
                                                                      activate_persist_through_power_loss=1,
                                                                      relative_target_port_identifier=7,
                                                                      transport_id_length=transport_id_length,
                                                                      transport_id=transport_id)
        self.assertEquals(obj.pack(), PRO_READ_RESERVATIONS_REGISTER_AND_MOVE_PARAMETERS_SAMPLE)
