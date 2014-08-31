import sys
from infi.asi import create_platform_command_executer
from infi.asi.cdb.inquiry.standard import StandardInquiryCommand
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.asi import create_os_file
from infi.exceptools import print_exc

if len(sys.argv) != 2:
    sys.stderr.write("usage: %s device_name\n" % sys.argv[0])
    sys.exit(1)

path = sys.argv[1]

f = create_os_file(path)

try:
    executer = create_platform_command_executer(f)

    inquiry = StandardInquiryCommand()
    data = sync_wait(inquiry.execute(executer))

    print(data)

    f.close()
except:
    print_exc()
