import unittest

class BlockLimitsTestCase(unittest.TestCase):
    def test_import(self):
        from infi.asi.cdb.inquiry.vpd_pages import block_limits

    def test_parsing(self):
        # TODO find a real response
        from infi.asi.cdb.inquiry.vpd_pages import block_limits
        response = '\x00' * 64
        block_limits.BlockLimitsVPDPageData.create_from_string(response)

    def test_supported_pages(self):
        from infi.asi.cdb.inquiry.vpd_pages import SUPPORTED_VPD_PAGES_COMMANDS
        from infi.asi.cdb.inquiry.vpd_pages import block_limits
        self.assertIs(SUPPORTED_VPD_PAGES_COMMANDS[0xb0],
                      block_limits.BlockLimitsPageCommand)

