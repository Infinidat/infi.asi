from __future__ import print_function
import sys
from infi.asi import create_platform_command_executer
from infi.asi.cdb.diagnostic import ses_pages
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.exceptools import print_exc
from infi.asi import create_os_file


available_commands = {
    "0x01": ses_pages.ConfigurationDiagnosticPagesCommand,
    "0x02": ses_pages.EnclosureStatusDiagnosticPagesCommand,
    "0x07": ses_pages.ElementDescriptorDiagnosticPagesCommand,
}


def run_cmd(os_file, cmd, helper=None):
    executer = create_platform_command_executer(os_file)
    cdb = cmd(helper) if helper else cmd()
    data = sync_wait(cdb.execute(executer))
    return data


def doit(dev, page):
    f = create_os_file(dev)
    command = available_commands[page]
    if page in ('0x02', '0x07'):
        cfg_data = run_cmd(f, ses_pages.ConfigurationDiagnosticPagesCommand)
        data = run_cmd(f, command, cfg_data)
    else:
        data = run_cmd(f, command)
    f.close()
    return data


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("usage: %s device_name ses_command\n" % sys.argv[0])
        sys.exit(1)

    try:
        if sys.argv[2] not in available_commands:
            raise ValueError("available commands: %s" % repr(available_commands.keys()))

        data = doit(sys.argv[1], sys.argv[2])
        print(repr(data))
    except:
        print_exc()
