from __future__ import print_function
import platform
import sys
from infi.asi import create_platform_command_executer
from infi.asi.cdb.inquiry import StandardInquiryCommand, SupportedVPDPagesCommand, \
        UnitSerialNumberVPDPageCommand, DeviceIdentificationVPDPageCommand
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.exceptools import print_exc


if len(sys.argv) != 3:
    sys.stderr.write("usage: %s device_name inquiry_command\n" % sys.argv[0])
    sys.exit(1)

path = sys.argv[1]

if platform.system() == 'Windows':
    from infi.asi.win32 import OSFile
    f = OSFile(path)
else:
    import os
    from infi.asi.unix import OSFile
    f = OSFile(os.open(path, os.O_RDWR))

available_commands = {
                      "standard": StandardInquiryCommand,
                      "0x80": UnitSerialNumberVPDPageCommand,
                      "0x83": DeviceIdentificationVPDPageCommand,
                      }

if sys.argv[2] not in available_commands:
    print ("available commands: %s" % repr(available_commands.keys()))
command = available_commands[sys.argv[2]]

try:
    executer = create_platform_command_executer(f)
    cdb = command.create()
    data = sync_wait(cdb.execute(executer))

    # print(data), __str__ is broken
    print(repr(data))

    f.close()
except:
    print_exc()

