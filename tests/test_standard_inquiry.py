import unittest
import binascii
from infi.unittest import TestCase

from infi.asi.cdb.inquiry.standard import StandardInquiryDataBuffer, PeripheralDeviceDataBuffer


def hex_to_bin(s):
    return bytearray(binascii.unhexlify(s.replace(' ', '')))


class StandardInquiryTestCase(TestCase):
    def test_unpack__sas_drive(self):
        # sg_inq -v /dev/sg161
        #     inquiry cdb: 12 00 00 00 24 00
        # standard INQUIRY:
        #     inquiry cdb: 12 00 00 00 a4 00
        #   PQual=0  Device_type=0  RMB=0  version=0x05  [SPC-3]
        #   [AERC=0]  [TrmTsk=0]  NormACA=0  HiSUP=0  Resp_data_format=2
        #   SCCS=0  ACC=0  TPGS=0  3PC=0  Protect=0  [BQue=0]
        #   EncServ=0  MultiP=1 (VS=0)  [MChngr=0]  [ACKREQQ=0]  Addr16=0
        #   [RelAdr=0]  WBus16=0  Sync=0  Linked=0  [TranDis=0]  CmdQue=1
        #   [SPI: Clocking=0x0  QAS=0  IUS=0]
        #     length=164 (0xa4)   Peripheral device type: disk
        #  Vendor identification: ATA
        #  Product identification: Hitachi HDP72505
        #  Product revision level: A5CA
        #     inquiry cdb: 12 01 00 00 fc 00
        #     inquiry: pass-through requested 252 bytes but got 11 bytes
        #     inquiry cdb: 12 01 80 00 fc 00
        #     inquiry: pass-through requested 252 bytes but got 24 bytes
        #  Unit serial number:       GEA534RV0X6SPA
        raw_data = hex_to_bin(
            "00 00 05 02 9f 00 10 02  41 54 41 20 20 20 20 20" +
            "48 69 74 61 63 68 69 20  48 44 50 37 32 35 30 35" +
            "41 35 43 41 47 45 41 35  33 34 52 56 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 60 1e c0 03 00" +
            "04 c0 0c 00 0c 20 16 00  16 23 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 02 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00" +
            "00 00 00 00")
        data = StandardInquiryDataBuffer()
        data.unpack(raw_data)
        self.assertEqual(data.additional_length, 0x9f)
        self.assertEqual(data.t10_vendor_identification, "ATA")
        self.assertEqual(data.product_identification, "Hitachi HDP72505")
        self.assertEqual(data.product_revision_level, "A5CA")
        self.assertEqual(data.extended.version_descriptors,
                          [0x0060, 0x1ec0, 0x0300, 0x04c0, 0x0c00, 0xc20, 0x1600, 0x1623])


    def test_unpack__enclosure(self):
        # sg_inq -v /dev/sg160
        #     inquiry cdb: 12 00 00 00 24 00
        # standard INQUIRY:
        #   PQual=0  Device_type=13  RMB=0  version=0x03  [SPC]
        #   [AERC=0]  [TrmTsk=0]  NormACA=0  HiSUP=0  Resp_data_format=2
        #   SCCS=0  ACC=0  TPGS=0  3PC=0  Protect=0  [BQue=0]
        #   EncServ=1  MultiP=0  [MChngr=0]  [ACKREQQ=0]  Addr16=0
        #   [RelAdr=0]  WBus16=0  Sync=0  Linked=0  [TranDis=0]  CmdQue=0
        #     length=36 (0x24)   Peripheral device type: enclosure services device
        #  Vendor identification: SAS E
        #  Product identification: x28-05.75.B002
        #  Product revision level: 000
        #     inquiry cdb: 12 01 00 00 fc 00
        # inquiry:  Fixed format, current;  Sense key: Illegal Request
        #  Additional sense: Invalid field in cdb
        raw_data = hex_to_bin(
            "0d 00 03 02 1f 00 40 00  53 41 53 20 45 20 20 20" +
            "78 32 38 2d 30 35 2e 37  35 2e 42 30 30 32 20 20" +
            "30 30 30 20")
        data = StandardInquiryDataBuffer()
        data.unpack(raw_data)
        print(repr(data))


    def test_pack__enclosure_no_extended_data(self):
        data = StandardInquiryDataBuffer(peripheral_device=PeripheralDeviceDataBuffer(qualifier=0, type=13),
                                         acc=0, cong=0, additional_length=31, addr16=0, cmd_que=0, enc_serv=1, hisup=0,
                                         multi_p=0, normaca=0, product_identification=u'x28-05.75.B002',
                                         product_revision_level=u'000', protect=0,
                                         response_data_format=2, rmb=0, sccs=0, sync=0,
                                         t10_vendor_identification=u'SAS E', threepc=0, tpgs=0, version=3, wbus16=0)
        packed_data = data.pack()
        raw_data = hex_to_bin(
            "0d 00 03 02 1f 00 40 00  53 41 53 20 45 20 20 20" +
            "78 32 38 2d 30 35 2e 37  35 2e 42 30 30 32 20 20" +
            "30 30 30 20")
        self.assertEqual(raw_data, packed_data)