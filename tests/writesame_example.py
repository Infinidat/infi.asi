import sys
from infi.asi import create_platform_command_executer
from infi.asi.cdb.write_same import  WriteSame10Command
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.asi import create_os_file
from infi.exceptools import print_exc

if len(sys.argv) not in (5, 6):
    sys.stderr.write("usage: %s device_name offset number_of_blocks cdb_size block\n" % sys.argv[0])
    sys.exit(1)

path, offset, number_of_blocks, cdb_size , file_for_block= (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),sys.argv[5] )

f = create_os_file(path)

try:

    executer = create_platform_command_executer(f)
    possible_commands = {10: WriteSame10Command}
    cdb = possible_commands[cdb_size](offset, open(file_for_block,'r').read(),number_of_blocks )
    sync_wait(cdb.execute(executer))
    f.close()
except:
    print_exc()
