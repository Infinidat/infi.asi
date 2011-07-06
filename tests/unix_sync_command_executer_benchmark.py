import os
import time
from infi.asi import create_platform_command_executer
from infi.asi.unix import OSFile
from infi.asi.cdb.inquiry import StandardInquiryData, StandardInquiryCommand
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.exceptools import print_exc

try:
    f = OSFile(os.open("/dev/sg0", os.O_RDWR))
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
