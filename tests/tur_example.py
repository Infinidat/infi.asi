import platform
import sys
from infi.asi import create_platform_command_executer
from infi.asi.cdb.tur import TestUnitReadyCommand
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
    tur = TestUnitReadyCommand.create()
    data = sync_wait(tur.execute(executer))

    print(data)

    f.close()
except:
    print_exc()

