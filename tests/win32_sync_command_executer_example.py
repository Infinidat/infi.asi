import os
from infi.asi import create_platform_command_executer
from infi.asi.win32 import OSFile
from infi.asi.cdb.inquiry import StandardInquiryData, StandardInquiryCommand
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.exceptools import print_exc

try:
    f = OSFile(r"\\.\PHYSICALDRIVE0",
               OSFile.GENERIC_READ | OSFile.GENERIC_WRITE,
               OSFile.FILE_SHARE_READ | OSFile.FILE_SHARE_WRITE,
               OSFile.OPEN_EXISTING)
    executer = create_platform_command_executer(f)

    inquiry = StandardInquiryCommand.create()
    data = sync_wait(inquiry.execute(executer))

    print(data)

    f.close()
except:
    print_exc()
