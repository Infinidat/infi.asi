def test_report_luns():
    from infi.asi.unix import OSFile
    import os
    if not os.path.exists("/dev/sg1"):
        return
    from infi.asi.coroutines.sync_adapter import sync_wait
    from infi.asi.cdb.report_luns import ReportLunsCommand
    from infi.asi import create_platform_command_executer
    handle = OSFile(os.open("/dev/sg1", os.O_RDWR))
    executer = create_platform_command_executer(handle)
    cdb = ReportLunsCommand(select_report=0)
    result = sync_wait(cdb.execute(executer))
    assert result.lun_list != []
    assert 0 in result.lun_list
