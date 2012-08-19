import platform
from infi.asi import create_platform_command_executer
from infi.asi.cdb.compare_and_write import CompareAndWriteCommand
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.exceptools import print_exc
import sys

(path, offset, compare_buffer_path, write_buffer_path)  = (sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])

if platform.system() == 'Windows':
    from infi.asi.win32 import OSFile
    f = OSFile(path)
else:
    import os
    from infi.asi.unix import OSFile
    f = OSFile(os.open(path, os.O_RDWR))

with open(compare_buffer_path) as p:
    compare_buffer=p.read()
with open(write_buffer_path) as p:
    write_buffer=p.read()

try:

    executer = create_platform_command_executer(f)
    cdb = CompareAndWriteCommand(logical_block_address=offset, buffer=compare_buffer + write_buffer, number_of_logical_blocks=1)
    sync_wait(cdb.execute(executer))
    f.close()
except:
    print_exc()

