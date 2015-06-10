from infi.asi import create_platform_command_executer, create_os_file
from infi.pyutils.contexts import contextmanager


MS = 1000
SG_TIMEOUT_IN_SEC = 3
SG_TIMEOUT_IN_MS = SG_TIMEOUT_IN_SEC * MS


@contextmanager
def windows(device):
    handle = create_os_file(device)
    executer = create_platform_command_executer(handle)
    try:
        yield executer
    finally:
        handle.close()


@contextmanager
def linux_dm(device):
    from infi.asi.linux import LinuxIoctlCommandExecuter

    handle = create_os_file(device)
    executer = LinuxIoctlCommandExecuter(handle)
    try:
        yield executer
    finally:
        handle.close()


@contextmanager
def linux_sg(device):
    handle = create_os_file(device)
    executer = create_platform_command_executer(handle, timeout=SG_TIMEOUT_IN_MS)
    try:
        yield executer
    finally:
        handle.close()


@contextmanager
def solaris(device):
    handle = create_os_file(device)
    executer = create_platform_command_executer(handle)
    try:
        yield executer
    finally:
        handle.close()


@contextmanager
def aix(device):
    handle = create_os_file(device)
    executer = create_platform_command_executer(handle)
    try:
        yield executer
    finally:
        handle.close()
