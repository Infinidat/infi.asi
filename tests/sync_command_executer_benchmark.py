import platform
import sys
import time
from infi.asi import create_platform_command_executer
from infi.asi.unix import OSFile
from infi.asi.cdb.inquiry import StandardInquiryData, StandardInquiryCommand
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.exceptools import print_exc

if len(sys.argv) != 2:
    sys.stderr.write("usage: %s device_name\n" % sys.argv[0])
    sys.exit(1)

path = sys.argv[1]

if platform.system() == 'Windows':
    from infi.asi.win32 import OSFile
    f = OSFile(path,
               OSFile.GENERIC_READ | OSFile.GENERIC_WRITE,
               OSFile.FILE_SHARE_READ | OSFile.FILE_SHARE_WRITE,
               OSFile.OPEN_EXISTING)
else:
    import os
    from infi.asi.unix import OSFile
    f = OSFile(os.open(path, os.O_RDWR))

try:
    executer = create_platform_command_executer(f)

    iters = 1000
    start_time = time.clock()
    for i in xrange(iters):
        inquiry = StandardInquiryCommand.create()
        data = sync_wait(inquiry.execute(executer))
    duration = time.clock() - start_time

    print("iters=%d, iters/sec: %.2f" % (iters, float(iters) / duration))

    print(data)

    f.close()
except:
    print_exc()
