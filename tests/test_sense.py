from infi.asi.sense import SCSISenseDataFixed, SCSI_SENSE_KEY
from infi.exceptools import print_exc

import binascii

def test_illegal_request():
    data = SCSISenseDataFixed.create_from_string(binascii.unhexlify("f00005000000000a00000000240000c00002"))
    assert data.response_code.code == 0x70
    assert data.response_code.valid == 1
    assert data.sense_key == 'ILLEGAL_REQUEST', data.sense_key

def test_tur():
    sense = binascii.unhexlify("f00002000000000a000000003a00000000")
    data = SCSISenseDataFixed.create_from_string(sense)
    assert data.response_code.code == 0x70
    assert data.response_code.valid == 1
    assert data.ili == 0 and data.eom == 0 and data.filemark == 0
    assert data.sense_key == 'NOT_READY', data.sense_key
    assert data.additional_sense_code.code_name == "MEDIUM NOT PRESENT", data.additional_sense_code.code_name
    assert data.additional_sense_length == 10
    assert data.field_replaceable_unit_code == 0
    assert data.sense_key_specific_high == 0 and data.sense_key_specific_low == 0
    assert data.sksv == 0

def test_sense():
    data = SCSISenseDataFixed.create_from_string(binascii.unhexlify("700006000000000A00000000290200000000"))
    assert data.response_code.code == 0x70
    assert data.response_code.valid == 0
    assert data.sense_key == 'UNIT_ATTENTION', data.sense_key

def test_sense2():
    # http://johnmeister.com/CS/UNIX/HP-UX/event-monitor-example.html
    data = SCSISenseDataFixed.create_from_string(binascii.unhexlify("700005000000000A00000000240000C80001"))
    assert repr(data) == "SCSISenseDataFixed(response_code=SCSISenseResponseCode(code=112, valid=0), <1 bytes padding>, sense_key='ILLEGAL_REQUEST', <1 bits padding>, ili=0, eom=0, filemark=0, information=0, additional_sense_length=10, command_specific_information=0, additional_sense_code=AdditionalSenseCode(INVALID FIELD IN CDB: code=0x24, qualifier=0x00), field_replaceable_unit_code=0, sense_key_specific_high=72, sksv=1, sense_key_specific_low=0)", repr(data)

# http://forums.support.roxio.com/topic/74314-tape-media-set-bad-media/
# 70 00 03 00 00 00 00 1e 00 00 00 00 3b 08 00 00 03 9c
