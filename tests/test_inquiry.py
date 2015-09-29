from __future__ import print_function

import unittest
import binascii
from glob import glob
from infi.unittest import TestCase
from infi.unittest.parameters import iterate
from infi.asi.cdb.inquiry.standard import StandardInquiryCommand
from infi.asi.cdb.inquiry.vpd_pages import UnitSerialNumberVPDPageCommand, DeviceIdentificationVPDPageCommand
from infi.asi.cdb.inquiry.vpd_pages import SupportedVPDPagesCommand


def hex_to_bin(s):
    return binascii.unhexlify(s.replace(' ', ''))

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
        from infi.asi.unix import UnixFile

        for scsi_id_path in glob('/sys/class/scsi_disk/*'):
            if scsi_id_path.split('/')[-1] == path.split('/')[-1]:
                block_device = glob(scsi_id_path + '/device/block/*')[0].split('/')[-1]
                if not block_device.startswith('sd'):
                    raise unittest.SkipTest()
                break

        f = UnixFile(open(path, O_RDWR))
        executer = create_platform_command_executer(f)
        cdb = command()
        try:
            _ = sync_wait(cdb.execute(executer))
        except AsiCheckConditionError as e:
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
        from infi.asi.cdb.inquiry.vpd_pages.device_identification import  DeviceIdentificationVPDPageBuffer
        buffer = b'\x00\x83\x00$\x01\x03\x00\x10`\x00@ \x01\xf4^\xb5f\xd4\x1c\xc3\x00\x00\x00\x00\x01\x14\x00\x04\x00\x00\x00\x02\x01\x15\x00\x04\x00\x00\x00\x02'
        obj = DeviceIdentificationVPDPageBuffer()
        obj.unpack(buffer)
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
        from infi.asi.cdb.inquiry.vpd_pages.device_identification import  DeviceIdentificationVPDPageBuffer
        buffer = b'\x00\x83\x00d\x01\x03\x00\x08WB\xb0\xf0\x100\x00\x00\x02\x00\x00\x13ip=251.252.253.254\x00\x01\x14\x00\x04\x00\x00 \x03\x01\x15\x00\x04\x00\x00 \x03\x03\x08\x00\x1dhost=just_for_test_host_name\x00\x03\x08\x00\x0cvol=VGX15S \x00'
        from logging import debug; debug(len(buffer))
        obj = DeviceIdentificationVPDPageBuffer()
        obj.unpack(buffer)
        self.assertEqual(len(obj.designators_list), 6)

    def test__serial_number(self):
        """
        00     0c 80 00 20 37 34 32 62  30 66 30 30 30 30 30 37    ... 742b0f000007
        10     35 33 36 30 30 30 30 30  30 30 30 30 30 30 30 30    5360000000000000
        20     30 30 30 00                                         000.
        """
        from infi.asi.cdb.inquiry.vpd_pages.unit_serial_number import UnitSerialNumberVPDPageBuffer
        buffer = b'\x0c\x80\x00\x20\x37\x34\x32\x62\x30\x66\x30\x30\x30\x30\x30\x37\x35\x33\x36\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x00'
        from logging import debug; debug(len(buffer))
        obj = UnitSerialNumberVPDPageBuffer()
        obj.unpack(buffer)
        self.assertEquals(obj.product_serial_number, '742b0f0000075360000000000000000')


class AtaInformation(TestCase):
    def test__ata_information(self):
        # VPD INQUIRY: ATA information page
        #   SAT Vendor identification: linux
        #   SAT Product identification: libata
        #   SAT Product revision level: ST6O
        #   Signature (Device to host FIS):
        #  00     34 80 40 00 01 00 00 00  00 00 00 00 01 00 00 00
        #  10     00 00 00 00
        #   ATA command IDENTIFY DEVICE response summary:
        #     model: Hitachi HDE721010SLA330
        #     serial number:       STR607MS2APNLS
        #     firmware revision: ST6OA3AA
        #   response in hex:
        #  00     045a 3fff c837 0010 0000 0000 003f 0000     .Z ?. .7 .. .. .. .? ..
        #  08     0000 0000 2020 2020 2020 5354 5236 3037     .. ..          ST R6 07
        #  10     4d53 3241 504e 4c53 0003 f152 0038 5354     MS 2A PN LS .. .R .8 ST
        #  18     364f 4133 4141 4869 7461 6368 6920 4844     6O A3 AA Hi ta ch i  HD
        #  20     4537 3231 3031 3053 4c41 3333 3020 2020     E7 21 01 0S LA 33 0
        #  28     2020 2020 2020 2020 2020 2020 2020 8010                          ..
        #  30     4000 2f00 4000 0200 0200 0007 3fff 0010     @. /. @. .. .. .. ?. ..
        #  38     003f fc10 00fb 0110 ffff 0fff 0000 0007     .? .. .. .. .. .. .. ..
        #  40     0003 0078 0078 0078 0078 0000 0000 0000     .. .x .x .x .x .. .. ..
        #  48     0000 0000 0000 001f 1706 0000 005e 0040     .. .. .. .. .. .. .^ .@
        #  50     01fc 0029 346b 7fe9 4773 3469 be01 4763     .. .) 4k .. Gs 4i .. Gc
        #  58     407f 00a2 0000 0000 fffe 0000 80fe 0008     @. .. .. .. .. .. .. ..
        #  60     00ca 00f9 2710 0000 6db0 7470 0000 0000     .. .. '. .. m. tp .. ..
        #  68     00ca 0000 0000 5a87 5000 cca3 5ee1 0c0b     .. .. .. Z. P. .. ^. ..
        #  70     0000 0000 0000 0000 0000 0000 0000 4014     .. .. .. .. .. .. .. @.
        #  78     4014 0000 0000 0000 0000 0000 0000 0000     @. .. .. .. .. .. .. ..
        #  80     0009 000b 0000 0000 2980 0db1 fe20 0001     .. .. .. .. ). .. .  ..
        #  88     4000 0404 8531 0000 0000 0605 0503 0603     @. .. .1 .. .. .. .. ..
        #  90     0504 0603 0305 5cff ac8a 44c8 8000 0000     .. .. .. \. .. D. .. ..
        #  98     3658 4333 0000 e806 0000 0000 0000 0000     6X C3 .. .. .. .. .. ..
        #  a0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  a8     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  b0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  b8     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  c0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  c8     0000 0000 0000 0000 0000 0000 003d 0000     .. .. .. .. .. .. .= ..
        #  d0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  d8     0000 1c20 0000 0000 0000 0000 101f 0021     .. .  .. .. .. .. .. .!
        #  e0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  e8     0000 0000 0001 03e0 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  f0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  f8     0000 0000 0000 0000 0000 0000 0000 42a5     .. .. .. .. .. .. .. B.
        raw_data = hex_to_bin(
            "00 89 02 38 00 00 00 00  6c 69 6e 75 78 20 20 20" +
            "6c 69 62 61 74 61 20 20  20 20 20 20 20 20 20 20" +
            "53 54 36 4f 34 80 40 00  01 00 00 00 00 00 00 00" +
            "01 00 00 00 00 00 00 00  ec 00 00 00 5a 04 ff 3f" +
            "37 c8 10 00 00 00 00 00  3f 00 00 00 00 00 00 00" +
            "20 20 20 20 20 20 54 53  36 52 37 30 53 4d 41 32" +
            "4e 50 53 4c 03 00 52 f1  38 00 54 53 4f 36 33 41" +
            "41 41 69 48 61 74 68 63  20 69 44 48 37 45 31 32" +
            "31 30 53 30 41 4c 33 33  20 30 20 20 20 20 20 20" +
            "20 20 20 20 20 20 20 20  20 20 10 80 00 40 00 2f" +
            "00 40 00 02 00 02 07 00  ff 3f 10 00 3f 00 10 fc" +
            "fb 00 10 01 ff ff ff 0f  00 00 07 00 03 00 78 00" +
            "78 00 78 00 78 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 1f 00 06 17 00 00  5e 00 40 00 fc 01 29 00" +
            "6b 34 e9 7f 73 47 69 34  01 be 63 47 7f 40 a2 00" +
            "00 00 00 00 fe ff 00 00  fe 80 08 00 ca 00 f9 00" +
            "10 27 00 00 b0 6d 70 74  00 00 00 00 ca 00 00 00" +
            "00 00 87 5a 00 50 a3 cc  e1 5e 0b 0c 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 14 40 14 40 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 09 00 0b 00" +
            "00 00 00 00 80 29 b1 0d  20 fe 01 00 00 40 04 04" +
            "31 85 00 00 00 00 05 06  03 05 03 06 04 05 03 06" +
            "05 03 ff 5c 8a ac c8 44  00 80 00 00 58 36 33 43" +
            "00 00 06 e8 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  3d 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 20 1c" +
            "00 00 00 00 00 00 00 00  1f 10 21 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "01 00 e0 03 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 a5 42")
        from infi.asi.cdb.inquiry.vpd_pages.ata_information import AtaInformationVPDPageBuffer
        obj = AtaInformationVPDPageBuffer()
        obj.unpack(raw_data)
        self.assertEquals(obj.sat_vendor_identification, 'linux')
        self.assertEquals(obj.sat_product_identification, 'libata')
        self.assertEquals(obj.sat_product_revision_level, 'ST6O')
        self.assertEquals(obj.identify_device.firmware_revision, 'ST6OA3AA')
        self.assertEquals(obj.identify_device.serial_number, '      STR607MS2APNLS')
        self.assertEquals(obj.identify_device.model_number, 'Hitachi HDE721010SLA330')


    def test__ata_information_2(self):
        # VPD INQUIRY: ATA information page
        #   SAT Vendor identification: LSI
        #   SAT Product identification: LSISS25x0
        #   SAT Product revision level: 0000
        #   Signature (Device to host FIS):
        #  00     34 40 50 01 01 00 00 00  00 00 00 00 01 00 00 00
        #  10     00 00 00 00
        #   ATA command IDENTIFY DEVICE response summary:
        #     model: Hitachi HUA722010CLA330
        #     serial number:       JPW9K0HD26WMHL
        #     firmware revision: JP4OA3EA
        #   response in hex:
        #  00     045a 3fff c837 0010 0000 0000 003f 0000     .Z ?. .7 .. .. .. .? ..
        #  08     0000 0000 2020 2020 2020 4a50 5739 4b30     .. ..          JP W9 K0
        #  10     4844 3236 574d 484c 0003 ea5f 0038 4a50     HD 26 WM HL .. ._ .8 JP
        #  18     344f 4133 4541 4869 7461 6368 6920 4855     4O A3 EA Hi ta ch i  HU
        #  20     4137 3232 3031 3043 4c41 3333 3020 2020     A7 22 01 0C LA 33 0
        #  28     2020 2020 2020 2020 2020 2020 2020 8010                          ..
        #  30     4000 2f00 4000 0200 0200 0007 3fff 0010     @. /. @. .. .. .. ?. ..
        #  38     003f fc10 00fb 0100 ffff 0fff 0000 0407     .? .. .. .. .. .. .. ..
        #  40     0003 0078 0078 0078 0078 0000 0000 0000     .. .x .x .x .x .. .. ..
        #  48     0000 0000 0000 001f 1706 0000 005e 0040     .. .. .. .. .. .. .^ .@
        #  50     01fc 0029 346b 7d69 4773 3449 bc41 4763     .. .) 4k }i Gs 4I .A Gc
        #  58     007f 0074 0000 0000 fffe 0000 0000 0008     .. .t .. .. .. .. .. ..
        #  60     00ca 00f9 2710 0000 6db0 7470 0000 0000     .. .. '. .. m. tp .. ..
        #  68     00ca 0000 0000 5a87 5000 cca3 73df 50f3     .. .. .. Z. P. .. s. P.
        #  70     0000 0000 0000 0000 0000 0000 0000 4014     .. .. .. .. .. .. .. @.
        #  78     4014 0000 0000 0000 0000 0000 0000 0000     @. .. .. .. .. .. .. ..
        #  80     0001 000b 0000 0000 2080 0df1 fa20 0001     .. .. .. ..  . .. .  ..
        #  88     4000 0404 026a 0000 0000 0706 0706 0506     @. .. .j .. .. .. .. ..
        #  90     0609 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  98     3437 4833 0000 7804 0000 5dbd a1d3 8000     47 H3 .. x. .. ]. .. ..
        #  a0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  a8     0002 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  b0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  b8     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  c0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  c8     0000 0000 0000 0000 0000 0000 003d 0000     .. .. .. .. .. .. .= ..
        #  d0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  d8     0000 1c20 0000 0000 0000 0000 101f 0021     .. .  .. .. .. .. .. .!
        #  e0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  e8     0000 0000 0001 03e0 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  f0     0000 0000 0000 0000 0000 0000 0000 0000     .. .. .. .. .. .. .. ..
        #  f8     0000 0000 0000 0000 0000 0000 0000 19a5     .. .. .. .. .. .. .. ..
        raw_data = hex_to_bin(
             "00 89 02 38 00 00 00 00  4c 53 49 20 20 20 20 20" +
             "4c 53 49 53 53 32 35 78  30 20 20 20 20 20 20 20" +
             "30 30 30 30 34 40 50 01  01 00 00 00 00 00 00 00" +
             "01 00 00 00 00 00 00 00  ec 00 00 00 5a 04 ff 3f" +
             "37 c8 10 00 00 00 00 00  3f 00 00 00 00 00 00 00" +
             "20 20 20 20 20 20 50 4a  39 57 30 4b 44 48 36 32" +
             "4d 57 4c 48 03 00 5f ea  38 00 50 4a 4f 34 33 41" +
             "41 45 69 48 61 74 68 63  20 69 55 48 37 41 32 32" +
             "31 30 43 30 41 4c 33 33  20 30 20 20 20 20 20 20" +
             "20 20 20 20 20 20 20 20  20 20 10 80 00 40 00 2f" +
             "00 40 00 02 00 02 07 00  ff 3f 10 00 3f 00 10 fc" +
             "fb 00 00 01 ff ff ff 0f  00 00 07 04 03 00 78 00" +
             "78 00 78 00 78 00 00 00  00 00 00 00 00 00 00 00" +
             "00 00 1f 00 06 17 00 00  5e 00 40 00 fc 01 29 00" +
             "6b 34 69 7d 73 47 49 34  41 bc 63 47 7f 00 74 00" +
             "00 00 00 00 fe ff 00 00  00 00 08 00 ca 00 f9 00" +
             "10 27 00 00 b0 6d 70 74  00 00 00 00 ca 00 00 00" +
             "00 00 87 5a 00 50 a3 cc  df 73 f3 50 00 00 00 00" +
             "00 00 00 00 00 00 00 00  00 00 14 40 14 40 00 00" +
             "00 00 00 00 00 00 00 00  00 00 00 00 01 00 0b 00" +
             "00 00 00 00 80 20 f1 0d  20 fa 01 00 00 40 04 04" +
             "6a 02 00 00 00 00 06 07  06 07 06 05 09 06 00 00" +
             "00 00 00 00 00 00 00 00  00 00 00 00 37 34 33 48" +
             "00 00 04 78 00 00 bd 5d  d3 a1 00 80 00 00 00 00" +
             "00 00 00 00 00 00 00 00  00 00 00 00 02 00 00 00" +
             "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
             "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
             "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
             "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
             "00 00 00 00 00 00 00 00  3d 00 00 00 00 00 00 00" +
             "00 00 00 00 00 00 00 00  00 00 00 00 00 00 20 1c" +
             "00 00 00 00 00 00 00 00  1f 10 21 00 00 00 00 00" +
             "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
             "01 00 e0 03 00 00 00 00  00 00 00 00 00 00 00 00" +
             "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
             "00 00 00 00 00 00 00 00  00 00 a5 19")
        from infi.asi.cdb.inquiry.vpd_pages.ata_information import AtaInformationVPDPageBuffer
        obj = AtaInformationVPDPageBuffer()
        obj.unpack(raw_data)
        self.assertEquals(obj.sat_vendor_identification, 'LSI')
        self.assertEquals(obj.sat_product_identification, 'LSISS25x0')
        self.assertEquals(obj.sat_product_revision_level, '0000')
        self.assertEquals(obj.identify_device.firmware_revision, 'JP4OA3EA')
        self.assertEquals(obj.identify_device.serial_number, '      JPW9K0HD26WMHL')
        self.assertEquals(obj.identify_device.model_number, 'Hitachi HUA722010CLA330')
