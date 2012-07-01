from __future__ import print_function

import unittest
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

        # Make sure it's a disk (and not a CD-ROM) - disks should be sdX. We're traversing sysfs from the scsi_generic
        # to the block device.
        for scsi_id_path in glob('/sys/class/scsi_generic/*'):
            if scsi_id_path.split('/')[-1] == path.split('/')[-1]:
                block_device = glob(scsi_id_path + '/device/block/*')[0].split('/')[-1]
                if not block_device.startswith('sd'):
                    raise unittest.SkipTest()
                break

        f = OSFile(open(path, O_RDWR))
        executer = create_platform_command_executer(f)
        cdb = command()
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

class DeviceIdentification(TestCase):
    def test__recorded_example_1(self):
        """
        VPD INQUIRY: Device Identification page
  Designation descriptor number 1, descriptor length: 20
    designator_type: NAA,  code_set: Binary
    associated with the addressed logical unit
      NAA 6, IEEE Company_id: 0x402
      Vendor Specific Identifier: 0x1f45eb5
      Vendor Specific Identifier Extension: 0x66d41cc300000000
      [0x6000402001f45eb566d41cc300000000]
  Designation descriptor number 2, descriptor length: 8
    designator_type: Relative target port,  code_set: Binary
    associated with the target port
      Relative target port: 0x2
  Designation descriptor number 3, descriptor length: 8
    designator_type: Target port group,  code_set: Binary
    associated with the target port
      Target port group: 0x2
      """
        from infi.asi.cdb.inquiry.vpd_pages.device_identification import  DeviceIdentificationVPDPageData
        buffer = '\x00\x83\x00$\x01\x03\x00\x10`\x00@ \x01\xf4^\xb5f\xd4\x1c\xc3\x00\x00\x00\x00\x01\x14\x00\x04\x00\x00\x00\x02\x01\x15\x00\x04\x00\x00\x00\x02'
        obj = DeviceIdentificationVPDPageData.create_from_string(buffer)
        self.assertEqual(len(obj.designators_list), 3)

    def test__recorded_example_2(self):
        """
        VPD INQUIRY: Device Identification page
  Designation descriptor number 1, descriptor length: 12
    designator_type: NAA,  code_set: Binary
    associated with the addressed logical unit
      NAA 5, IEEE Company_id: 0x742b0f
      Vendor Specific Identifier: 0x10300000
      [0x5742b0f010300000]
  Designation descriptor number 2, descriptor length: 23
    designator_type: vendor specific [0x0],  code_set: ASCII
    associated with the addressed logical unit
      vendor specific: ip=251.252.253.254
  Designation descriptor number 3, descriptor length: 8
    designator_type: Relative target port,  code_set: Binary
    associated with the target port
      Relative target port: 0x2003
  Designation descriptor number 4, descriptor length: 8
    designator_type: Target port group,  code_set: Binary
    associated with the target port
      Target port group: 0x2003
  Designation descriptor number 5, descriptor length: 33
    designator_type: SCSI name string,  code_set: UTF-8
    associated with the addressed logical unit
      SCSI name string:
      host=just_for_test_host_name
  Designation descriptor number 6, descriptor length: 16
    designator_type: SCSI name string,  code_set: UTF-8
    associated with the addressed logical unit
      SCSI name string:
      vol=VGX15S """
        from infi.asi.cdb.inquiry.vpd_pages.device_identification import  DeviceIdentificationVPDPageData
        buffer = '\x00\x83\x00d\x01\x03\x00\x08WB\xb0\xf0\x100\x00\x00\x02\x00\x00\x13ip=251.252.253.254\x00\x01\x14\x00\x04\x00\x00 \x03\x01\x15\x00\x04\x00\x00 \x03\x03\x08\x00\x1dhost=just_for_test_host_name\x00\x03\x08\x00\x0cvol=VGX15S \x00'
        from logging import debug; debug(len(buffer))
        obj = DeviceIdentificationVPDPageData.create_from_string(buffer)
        self.assertEqual(len(obj.designators_list), 6)

    def test__serial_number(self):
        """
        00     0c 80 00 20 37 34 32 62  30 66 30 30 30 30 30 37    ... 742b0f000007
        10     35 33 36 30 30 30 30 30  30 30 30 30 30 30 30 30    5360000000000000
        20     30 30 30 00                                         000.        
        """
        from infi.asi.cdb.inquiry.vpd_pages.unit_serial_number import UnitSerialNumberVPDPageData
        buffer = '\x0c\x80\x00\x20\x37\x34\x32\x62\x30\x66\x30\x30\x30\x30\x30\x37\x35\x33\x36\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x00'
        from logging import debug; debug(len(buffer))
        obj = UnitSerialNumberVPDPageData.create_from_string(buffer)
        self.assertEquals(obj.product_serial_number, '742b0f0000075360000000000000000')
        
