import unittest
from infi.asi.cdb.inquiry.vpd_pages import logical_block_provisioning

class LogicalBlockProvisioningTestCase(unittest.TestCase):
    def unpack_page(self, page, packed_data, conf_page):
        page_class = get_ses_page(page)
        data_class = get_ses_page_data(page)

        data = data_class(conf_page=conf_page)
        data.unpack(hex_to_bin(packed_data))
        return data

    def test_without_provisioning_group_descriptor(self):
        response = b'\x00' * 8
        data = logical_block_provisioning.LogicalBlockProvisioningVPDPageBuffer()
        data.unpack(response)
        assert data.provisioning_group_descriptor == None

    def test_with_vendor_specific_provisioning_group_descriptor(self):
        response = b'\x00' * 8 + b'\x00' * 4
        data = logical_block_provisioning.LogicalBlockProvisioningVPDPageBuffer()
        data.unpack(response)
        assert data.provisioning_group_descriptor.vendor_specific_identifier == b''
