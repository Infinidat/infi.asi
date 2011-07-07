import platform
import sys
from infi.asi import create_platform_command_executer
from infi.asi.cdb.read import Read6Command, Read10Command
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.exceptools import print_exc

if len(sys.argv) != 5:
    sys.stderr.write("usage: %s device_name offset length cdb_size\n" % sys.argv[0])
    sys.exit(1)

path, offset, length, cdb_size = (sys.argv[1], int(sys.argv[2]),
                                  int(sys.argv[3]), int(sys.argv[4]))

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
    possible_commands = {6: Read6Command,
                         10: Read10Command}

    cdb = possible_commands[cdb_size].create(logical_block_address=offset,
                                             transfer_length=length)
    data = sync_wait(cdb.execute(executer))

    print(repr(data))

    f.close()
except:
    print_exc()

