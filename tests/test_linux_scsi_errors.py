from infi.asi.linux import LinuxCommandExecuter, SGIO, AsiSCSIError
from infi import unittest
from mock import patch
from ctypes import sizeof

SGIO_SIZE = sizeof(SGIO)

class Mock_SGIO(object):
    pack_id = 0
    status = 1
    driver_status = 0
    host_status = 0

    def read(self, size):
        return '\x00' * SGIO_SIZE

class StorageModel_110(unittest.TestCase):
    def test_os_receive__sgio_status_nonzero(self):
        io = Mock_SGIO()
        executer = LinuxCommandExecuter(io)
        with patch("infi.asi.linux.SGIO") as SGIO_:
            SGIO_.from_string.return_value = io
            response = [response for response in executer._os_receive()][1]
        error, packet_id = response
        self.assertIsInstance(error, AsiSCSIError)
