import binascii

from infi.asi.cdb.inquiry.vpd_pages.device_identification import DeviceIdentificationVPDPageData

"""
VPD INQUIRY: Device Identification page
  Designation descriptor number 1, descriptor length: 20
    designator_type: NAA,  code_set: Binary
    associated with the addressed logical unit
      NAA 6, IEEE Company_id: 0x402
      Vendor Specific Identifier: 0x1f45eb5
      Vendor Specific Identifier Extension: 0x66d41cd100000000
      [0x6000402001f45eb566d41cd100000000]
  Designation descriptor number 2, descriptor length: 8
    designator_type: Relative target port,  code_set: Binary
    associated with the target port
      Relative target port: 0x1
  Designation descriptor number 3, descriptor length: 8
    designator_type: Target port group,  code_set: Binary
    associated with the target port
      Target port group: 0x1
"""
def test_designator_1():
    raw_data = "00830024010300106000402001f45eb566d41cd10000000001140004000000010115000400000001"
    
    data = DeviceIdentificationVPDPageData.create_from_string(binascii.unhexlify(raw_data))
    print(repr(data))
