DATA = b'\x00\x00\x01X\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\r\x00\x00\x00\x00\x00\x00\x00\x0e\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x11\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x15\x00\x00\x00\x00\x00\x00\x00\x16\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00\x1a\x00\x00\x00\x00\x00\x00\x00\x1b\x00\x00\x00\x00\x00\x00\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x1d\x00\x00\x00\x00\x00\x00\x00\x1e\x00\x00\x00\x00\x00\x00\x00\x1f\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00"\x00\x00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00$\x00\x00\x00\x00\x00\x00\x00%\x00\x00\x00\x00\x00\x00\x00&\x00\x00\x00\x00\x00\x00\x00\'\x00\x00\x00\x00\x00\x00\x00(\x00\x00\x00\x00\x00\x00\x00)\x00\x00\x00\x00\x00\x00\x00*'

def test_report_luns_command():
    from infi.asi.unix import UnixFile
    import os
    if not os.path.exists("/dev/sg1"):
        return
    from infi.asi.coroutines.sync_adapter import sync_wait
    from infi.asi.cdb.report_luns import ReportLunsCommand
    from infi.asi import create_platform_command_executer
    handle = UnixFile(os.open("/dev/sg1", os.O_RDWR))
    executer = create_platform_command_executer(handle)
    cdb = ReportLunsCommand(select_report=0)
    result = sync_wait(cdb.execute(executer))
    assert result.lun_list != []
    assert 0 in result.lun_list

def test_report_luns_data():
   from infi.asi.cdb.report_luns import ReportLunsData
   data = ReportLunsData.create_from_string(DATA)
   assert data.lun_list == [i for i in range(0,43)]
