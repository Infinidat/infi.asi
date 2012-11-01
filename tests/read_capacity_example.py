import sys,os
import time
import platform
from infi.asi import create_platform_command_executer
from infi.asi.cdb.read_capacity import ReadCapacity10Command, ReadCapacity16Command
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.exceptools import print_exc

if len(sys.argv) != 3:
    sys.stderr.write("usage: %s device_name cdb_size\n" % sys.argv[0])
    sys.exit(1)

path, cdb_size = (sys.argv[1], int(sys.argv[2]))



class OSFile(object):
    def __init__(self, fd):
        self.fd = fd

    def read(self, size):
        return os.read(self.fd, size)

    def write(self, buffer):
        return os.write(self.fd, buffer)

    def close(self):
        os.close(self.fd)

f = OSFile(os.open(path, os.O_RDWR))
        
        
try:

    executer = create_platform_command_executer(f)
    possible_commands = {10: ReadCapacity10Command,
                         16: ReadCapacity16Command
                         }

    cdb = possible_commands[cdb_size](logical_block_address=0, pmi=0)
    data = sync_wait(cdb.execute(executer))

    print(repr(data))

    f.close()
except:
    print_exc()

