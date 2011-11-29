from __future__ import print_function
import platform
import sys
from infi.asi import create_platform_command_executer
from infi.asi.cdb.inquiry.standard import StandardInquiryCommand
from infi.asi.cdb.inquiry import vpd_pages
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.exceptools import print_exc


if len(sys.argv) != 3:
    sys.stderr.write("usage: %s device_name inquiry_command\n" % sys.argv[0])
    sys.exit(1)

try:
    available_commands = {
        "standard": StandardInquiryCommand,
        "0x80": vpd_pages.UnitSerialNumberVPDPageCommand,
        "0x83": vpd_pages.DeviceIdentificationVPDPageCommand,
    }

    if sys.argv[2] not in available_commands:
        raise ValueError("available commands: %s" % repr(available_commands.keys()))
            
    path = sys.argv[1]

    if platform.system() == 'Windows':
        from infi.asi.win32 import OSFile
        f = OSFile(path)
    else:
        import os
        from infi.asi.unix import OSFile
        f = OSFile(os.open(path, os.O_RDWR))

    command = available_commands[sys.argv[2]]

    executer = create_platform_command_executer(f)
    cdb = command.create()
    data = sync_wait(cdb.execute(executer))

    # print(data), __str__ is broken
    print(repr(data))

    f.close()
except:
    print_exc()
