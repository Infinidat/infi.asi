import unittest
from infi.asi.cdb.receive_copy_operating_parameters import (ReceiveCopyOperatingParametersCommand,
                                                            ReceiveCopyOperatingParametersResponse)

# root@qa-io-016:~# sg_copy_results /dev/sg5
# sg_copy_results: issue Receive copy operating parameters to device /dev/sg5
#                 xfer_len= 520 (0x208), list_id=0
#     Receive copy results [sa: operating parameters] cmd: 84 03 00 00 00 00 00 00 00 00 00 00 02 08 00 00
#     Receive copy results [sa: operating parameters]: pass-through requested 520 bytes but got 46 bytes
# Receive copy results (report operating parameters):
#     Supports no list identifier (SNLID): yes
#     Maximum target descriptor count: 2
#     Maximum segment descriptor count: 1
#     Maximum descriptor list length: 92 bytes
#     Maximum segment length: 0 bytes
#     Held data limit: 0 bytes
#     Maximum stream device transfer size: 0 bytes
#     Total concurrent copies: 8
#     Implemented descriptor list:
#         Segment descriptor 0x02: Copy from block device to block device
#         Target descriptor 0xe4: Identification descriptor
RECEIVE_COPY_OPERATING_PARAMETERS_CDB_DATA = b'\x84\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x08\x00\x00'

RECEIVE_COPY_OPERATING_PARAMETERS_RESPONSE_DATA = (b'\x00\x00\x00\x2a\x01\x00\x00\x00\x00\x02\x00\x01\x00\x00\x00\x5c' +
                                                   b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                                                   b'\x00\x00\x00\x08\x08\x10\x10\x10\x00\x00\x00\x02\x02\xe4\x2d\x61' +
                                                   b'\x67\x65\x3d\x30\x0d\x0a\x49\x66\x2d\x4d\x6f\x64\x69\x66\x69\x65' +
                                                   b'\x00\x50\x56\x99\x90\x64\x40\x55\x39\x24\x9e\xc1\x08\x00\x45\x10' +
                                                   b'\x00\x34\x2d\x39\x40\x00\x3f\x06\x42\xf1\xc0\xa8\x0a\x67\xac\x10' +
                                                   b'\x54\x6a\xd5\x43\x00\x16\x7e\xe4\xcc\xe0\x95\x4f\x47\xc5\x80\x10' +
                                                   b'\x01\x61\xd8\x8f\x00\x00\x01\x01\x08\x0a\x01\x42\xd4\xf9\x24\xf7' +
                                                   b'\xd7\xdb\x2f\xfb\xd4\x4c\xce\xbd\x2d\x23\x7e\x54\x42\x73\x1e\xb0' +
                                                   b'\xa1\x24\x9d\x62\xc9\x78\x4e\x74\xa7\x44\xad\xe2\x14\xfe\xec\xc4' +
                                                   b'\xc4\xe9\xd3\x66\x8d\x2e\x8a\x95\xee\x2a\x1c\x90\xc4\x89\x36\x06' +
                                                   b'\x78\x62\x65\x73\x73\x61\x67\x65\x49\x44\x3d\x22\x33\x4f\x43\x30' +
                                                   b'\x41\x43\x22\x2f\x3e\x2a\x53\x3d\xb7\x11\x94\x47\xa5\xa3\x26\x9e' +
                                                   b'\x71\x49\x74\x81\x7a\xeb\xcb\x2d\x27\xdf\x50\x80\xeb\xae\x8c\xc9' +
                                                   b'\x8b\xb0\x39\x98\x36\x6d\xfa\x18\xd0\x87\xde\xcb\xad\x94\x20\xe7' +
                                                   b'\x19\xdd\x56\x44\x2c\xb9\xd3\x51\x6a\xa4\xcc\x5b\xc7\xa2\x86\xda' +
                                                   b'\x37\x92\xaa\xdb\xab\x4a\xf3\xf9\x6f\x8b\xb5\x31\x85\x65\x50\x2d' +
                                                   b'\x53\xce\x30\x09\x6e\xd9\x49\xad\x2b\x34\x9e\xa4\x5b\x84\xfa\x69' +
                                                   b'\x96\x5e\x0e\x75\x6d\xdd\x07\x66\x25\x03\xa9\xb7\x4a\x03\x2e\xda' +
                                                   b'\x25\xe1\x4d\x1e\xf3\xab\x45\xb9\x8b\x8e\x0f\x33\xd0\x2b\x07\x2a' +
                                                   b'\x1d\x2a\xc0\x0f\x80\x9c\x5a\x23\x09\x5c\x49\x8a\xa2\x6c\xb3\x18' +
                                                   b'\x3c\xe6\x59\x48\x09\x21\x47\x7e\xeb\x7b\xe0\x00\x88\x46\x7e\x15' +
                                                   b'\x72\xeb\x80\xfa\xb4\x4e\xb5\x6f\xc9\x69\x5e\x83\xd0\x18\xe7\x39' +
                                                   b'\xe3\x71\x8b\x01\x0f\x5d\xdb\xc9\x84\x47\xbc\x9e\x67\x6e\x0a\x96' +
                                                   b'\xc1\xc9\x4b\x9d\xa2\x48\x35\xf5\xaa\x11\xf0\x3e\x0f\xb4\xb6\xc2' +
                                                   b'\x2b\x38\x9e\xc6\x7e\xe3\xf2\xed\xce\x84\x3a\x81\x27\xd2\x1e\xce' +
                                                   b'\xaa\xb5\x97\x4e\xec\x45\x85\xe3\xcb\x71\x81\xb3\x36\x9e\x0e\x95' +
                                                   b'\xa5\x11\xc1\x73\x3d\xcf\x47\x77\x2b\x3c\xe8\xca\x7d\x68\x0c\xeb' +
                                                   b'\x70\x6b\xab\x4d\x4b\xb7\xb1\x94\x78\xd1\xcc\x2f\x38\x7c\x01\x74' +
                                                   b'\x2c\xa4\x89\x5f\x47\x7b\xd0\xa0\xd3\x0e\x85\x58\x57\x78\xa9\x15' +
                                                   b'\x6e\x35\xdf\xb9\xc4\x01\x9a\xb3\xb3\x11\x5f\x72\x26\xdb\xd2\x97' +
                                                   b'\xee\xaa\x9f\x63\x1c\xf8\x57\xa3\x49\x90\xf3\x64\x53\xc7\xda\x68' +
                                                   b'\xa0\xed\x14\xdc\x86\xb1\x1f\x59')


class ReceiveCopyParametersTestCase(unittest.TestCase):
    def test_unpack_command(self):
        cmd = ReceiveCopyOperatingParametersCommand()
        cmd.unpack(RECEIVE_COPY_OPERATING_PARAMETERS_CDB_DATA)
        self.assertEquals(cmd.operation_code, 0x84)
        self.assertEquals(cmd.service_action, 3)
        self.assertEquals(cmd.allocation_length, 520)
        self.assertEquals(cmd.control, 0)

    def test_pack_command(self):
        cmd = ReceiveCopyOperatingParametersCommand(allocation_length=520, control=0)
        self.assertEquals(cmd.pack(), RECEIVE_COPY_OPERATING_PARAMETERS_CDB_DATA)

    def test_unpack_response(self):
        response = ReceiveCopyOperatingParametersResponse()
        response.unpack(RECEIVE_COPY_OPERATING_PARAMETERS_RESPONSE_DATA)
        self.assertEquals(response.available_data, 42)
        self.assertEquals(response.snlid, -1)
        self.assertEquals(response.max_cscd_descriptor_count, 2)
        self.assertEquals(response.max_segment_descriptor_count, 1)
        self.assertEquals(response.max_descriptor_list_length, 92)
        self.assertEquals(response.max_segment_length, 0)
        self.assertEquals(response.max_inline_data_length, 0)
        self.assertEquals(response.held_data_limit, 0)
        self.assertEquals(response.max_stream_device_transfer_size, 0)
        self.assertEquals(response.total_concurrent_copies, 8)
        self.assertEquals(response.max_concurrent_copies, 8)
        self.assertEquals(response.data_segment_granularity, 16)
        self.assertEquals(response.inline_data_granularity, 16)
        self.assertEquals(response.held_data_granularity, 16)
        self.assertEquals(response.implemented_descriptor_list_length, 2)
        self.assertEquals(response.implemented_descriptor_list, [2, 228])
