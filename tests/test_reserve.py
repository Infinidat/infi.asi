from infi.unittest import TestCase


class TestReserve6Command(TestCase):
    def test_generate_command(self):
        """
        Operation code (0x16)
        """
        from infi.asi.cdb.reserve import Reserve6Command
        obj = Reserve6Command()
        self.assertEqual(obj.pack(), b"\x16\x00\x00\x00\x00\x00")


class TestReserve10Command(TestCase):
    def test_generate_command_no_thirdparty(self):
        """
        Operation code (0x56)
        """
        from infi.asi.cdb.reserve import Reserve10Command
        obj = Reserve10Command(third_party_device_id=0)
        self.assertEqual(obj.pack(), b"\x56\x00\x00\x00\x00\x00\x00\x00\x00\x00")

    def test_generate_command_short_thirdparty(self):
        """
        Operation code (0x56)
        """
        from infi.asi.cdb.reserve import Reserve10Command
        obj = Reserve10Command(third_party_device_id=0x77)
        self.assertEqual(obj.pack(), b"\x56\x10\x00\x77\x00\x00\x00\x00\x00\x00")

    def test_generate_command_long_thirdparty(self):
        """
        Operation code (0x56)
        """
        from infi.asi.cdb.reserve import Reserve10Command
        obj = Reserve10Command(third_party_device_id=0x177)
        self.assertEqual(obj.pack(), b"\x56\x12\x00\x00\x00\x00\x00\x00\x08\x00")
        self.assertEqual(obj.parameter_list_datagram, b"\x00\x00\x00\x00\x00\x00\x01\x77")

    def test_generate_command_verylong_thirdparty(self):
        """
        Operation code (0x56)
        """
        from infi.asi.cdb.reserve import Reserve10Command
        obj = Reserve10Command(third_party_device_id=0xABABABABABABABAB)
        self.assertEqual(obj.pack(), b"\x56\x12\x00\x00\x00\x00\x00\x00\x08\x00")
        self.assertEqual(obj.parameter_list_datagram, b"\xAB\xAB\xAB\xAB\xAB\xAB\xAB\xAB")
