from __future__ import print_function

from glob import glob
from infi.unittest import TestCase
from infi.unittest.parameters import iterate
from infi.asi.cdb.inquiry.standard import StandardInquiryCommand
from infi.asi.cdb.inquiry.vpd_pages import UnitSerialNumberVPDPageCommand, DeviceIdentificationVPDPageCommand
from infi.asi.cdb.inquiry.vpd_pages import SupportedVPDPagesCommand

class LinuxInquiryTestCase(TestCase):
    def setUp(self):
        from platform import system
        if system() != "Linux":
            raise unittest.SkipTest()

    @iterate("command", [StandardInquiryCommand, UnitSerialNumberVPDPageCommand,
                         DeviceIdentificationVPDPageCommand, SupportedVPDPagesCommand])
    @iterate("path", glob("/dev/sg*"))
    def test_inquiry_command_on_path(self, path, command):
        from infi.asi import create_platform_command_executer, AsiCheckConditionError
        from infi.asi.coroutines.sync_adapter import sync_wait
        from os import open, O_RDWR
        from infi.asi.unix import OSFile
        f = OSFile(open(path, O_RDWR))
        executer = create_platform_command_executer(f)
        cdb = command.create()
        try:
            _ = sync_wait(cdb.execute(executer))
        except AsiCheckConditionError, e:
            # Some devices does not support some pages
            # for example, VMware on hba02 does not support 0x83
            if e.sense_obj.sense_key == 'ILLEGAL_REQUEST' \
                        and e.sense_obj.additional_sense_code.code_name == 'INVALID FIELD IN CDB':
                pass
            else:
                raise
        f.close()
