from infi.unittest import TestCase


class TestRelease6Command(TestCase):
    def test_generate_command(self):
        """
        Operation code (0x17)
        """
        from infi.asi.cdb.release import Release6Command
        obj = Release6Command()
        self.assertEquals(obj.pack(), b"\x17\x00\x00\x00\x00\x00")


class TestRelease10Command(TestCase):
    def test_generate_command_no_thirdparty(self):
        """
        Operation code (0x57)
        """
        from infi.asi.cdb.release import Release10Command
        obj = Release10Command(third_party_device_id=0)
        self.assertEquals(obj.pack(), b"\x57\x00\x00\x00\x00\x00\x00\x00\x00\x00")

    def test_generate_command_short_thirdparty(self):
        """
        Operation code (0x57)
        """
        from infi.asi.cdb.release import Release10Command
        obj = Release10Command(third_party_device_id=0x77)
        self.assertEquals(obj.pack(), b"\x57\x10\x00\x77\x00\x00\x00\x00\x00\x00")

    def test_generate_command_long_thirdparty(self):
        """
        Operation code (0x57)
        """
        from infi.asi.cdb.release import Release10Command
        obj = Release10Command(third_party_device_id=0x177)
        self.assertEquals(obj.pack(), b"\x57\x12\x00\x00\x00\x00\x00\x00\x08\x00")
        self.assertEquals(obj.parameter_list_datagram, b"\x00\x00\x00\x00\x00\x00\x01\x77")

    def test_generate_command_verylong_thirdparty(self):
        """
        Operation code (0x57)
        """
        from infi.asi.cdb.release import Release10Command
        obj = Release10Command(third_party_device_id=0xABABABABABABABAB)
        self.assertEquals(obj.pack(), b"\x57\x12\x00\x00\x00\x00\x00\x00\x08\x00")
        self.assertEquals(obj.parameter_list_datagram, b"\xAB\xAB\xAB\xAB\xAB\xAB\xAB\xAB")
