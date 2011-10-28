import unittest

class VeritasTestCase(unittest.TestCase):
    def test_import(self):
        from infi.asi.cdb.inquiry.vpd_pages import veritas

    def test_parsing(self):
        # TODO find a real response
        from infi.asi.cdb.inquiry.vpd_pages import veritas
        response = '\x00' * 6
        veritas.VeritasVPDPageData.create_from_string(response)

    def test_supported_pages(self):
        from infi.asi.cdb.inquiry.vpd_pages import SUPPORTED_VPD_PAGES_COMMANDS
        from infi.asi.cdb.inquiry.vpd_pages import veritas
        from infi.asi.cdb.inquiry.vpd_pages import block_limits
        self.assertIs(SUPPORTED_VPD_PAGES_COMMANDS[0xc0],
                      veritas.VeritasVPDPageCommand)

