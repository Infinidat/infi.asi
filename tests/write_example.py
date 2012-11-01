from infi.asi import create_platform_command_executer
from infi.asi.cdb.write import Write6Command, Write10Command
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.asi import create_os_file
from infi.exceptools import print_exc

if len(sys.argv) not in (5, 6):
    sys.stderr.write("usage: %s device_name offset length cdb_size [char='\x00']\n" % sys.argv[0])
    sys.exit(1)

path, offset, length, cdb_size = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
char = sys.argv[5][0] if len(sys.argv) == 6 else "\x00"

f = create_os_file(path)

try:

    executer = create_platform_command_executer(f)
    possible_commands = {6: Write6Command,
                         10: Write10Command}

    cdb = possible_commands[cdb_size](logical_block_address=offset, buffer=char * (length * 512))
    sync_wait(cdb.execute(executer))
    f.close()
except:
    print_exc()
