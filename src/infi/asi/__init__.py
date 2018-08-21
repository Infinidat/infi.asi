__import__("pkg_resources").declare_namespace(__name__)

import os
from infi.instruct import *
from infi.pyutils.decorators import wraps
from .errors import AsiException, AsiCheckConditionError, AsiInternalError
from .sense import *

try:
    from gevent import sleep as _gevent_friendly_sleep
except ImportError:
    _gevent_friendly_sleep = lambda *args, **kwargs: None

SCSI_STATUS_CODES = dict(
    SCSI_STATUS_GOOD                 = 0x00,
    SCSI_STATUS_CHECK_CONDITION      = 0x02,
    SCSI_STATUS_CONDITION_MET        = 0x04,
    SCSI_STATUS_BUSY                 = 0x08,
    SCSI_STATUS_RESERVATION_CONFLICT = 0x18,
    SCSI_STATUS_TASK_SET_FULL        = 0x28,
    SCSI_STATUS_ACA_ACTIVE           = 0x30,
    SCSI_STATUS_TASK_ABORTED         = 0x40
)

DEFAULT_MAX_QUEUE_SIZE = 15
DEFAULT_TIMEOUT_IN_SEC = 30
DEFAULT_TIMEOUT = DEFAULT_TIMEOUT_IN_SEC * 1000

class OSFile(object):
    pass

class OSAsyncFile(object):
    pass

class OSAsyncIOToken(object):
    def get_result(self, block=False):
        raise NotImplementedError()

class OSAsyncReactor(object):
    def wait_for(*commands):
        raise NotImplementedError()

class SCSICommand(object):
    def __init__(self, command):
        super(SCSICommand, self).__init__()
        self.command = command

class SCSIReadCommand(SCSICommand):
    def __init__(self, command, max_response_length):
        super(SCSIReadCommand, self).__init__(command)
        self.max_response_length = max_response_length

class SCSIWriteCommand(SCSICommand):
    def __init__(self, command, data):
        super(SCSIWriteCommand, self).__init__(command)
        self.data = data

class CommandExecuter(object):
    def call(self, command):
        raise NotImplementedError()

    def send(self, command, callback=None):
        raise NotImplementedError()

    def is_queue_full(self):
        raise NotImplementedError()

    def wait(self):
        raise NotImplementedError()

class CommandExecuterBase(CommandExecuter):
    def __init__(self, max_queue_size=DEFAULT_MAX_QUEUE_SIZE):
        self.pending_packets = dict()
        self.max_queue_size = max_queue_size
        self.packet_index = 0

    def call(self, command):
        result = []
        def my_cb(data, exception):
            result.append((data, exception))

        yield self.send(command, callback=my_cb)

        while len(result) == 0:
            yield self._process_pending_response()

        data, exception = result[0]
        if exception is not None:
            raise exception

        yield data

    def is_queue_full(self):
        return len(self.pending_packets) >= self.max_queue_size

    def is_queue_empty(self):
        return len(self.pending_packets) == 0

    def send(self, command, callback=None):
        packet_index = self._next_packet_index()

        os_data = self._os_prepare_to_send(command, packet_index)

        self.pending_packets[packet_index] = (os_data, callback)

        try:
            yield self._os_send(os_data)
        except:
            del self.pending_packets[packet_index]
            raise

    def wait(self):
        while not self.is_queue_empty():
            yield self._process_pending_response()

    def _next_packet_index(self):
        if len(self.pending_packets) >= self.max_queue_size:
            raise AsiRequestQueueFullError()
        result = self.packet_index
        self.packet_index = (self.packet_index + 1) % self.max_queue_size
        return result

    def _process_pending_response(self):
        if self.is_queue_empty():
            yield False

        result, packet_id = yield self._os_receive()

        request, callback = self.pending_packets.pop(packet_id, (None, None))
        if request is None:
            raise AsiInternalError("SCSI response doesn't appear in the pending I/O list.")

        if isinstance(result, Exception):
            callback(None, result)
        else:
            callback(result, None)

        yield True

    def _get_os_data(self, packet_index):
        return self.pending_packets.get(packet_index, (None, None))[0]

    def _os_prepare_to_send(self, command, packet_index):
        """Creates OS-specific data to send. Returns the opaque OS-specific data."""
        raise NotImplementedError()

    def _os_send(self, os_data):
        """Sends a packet prepared by _os_prepare_to_send()"""
        raise NotImplementedError()

    def _os_receive(self):
        """Returns the raw packet or an exception and packet_id as a pair: (packet, packet_id)"""
        raise NotImplementedError()

    def _check_condition(self, buf):
        sense = get_sense_object_from_buffer(buf)
        return AsiCheckConditionError(buf, sense)

# TODO: maybe add a ReactorCommandExecuter that also adds a "register_response_listener()" that automatically reads
# the responses and calls a callback.

class CommandExecuterAdapter(CommandExecuter):
    def __init__(self, executer, call_wrapper):
        super(CommandExecuterAdapter, self).__init__()
        self.executer = executer
        self.call_wrapper = call_wrapper

    def call(self, command):
        return self.call_wrapper(self.executer.call, command)

    def send(self, command, callback=None):
        return self.call_wrapper(self.executer.send, command, callback)

    def is_queue_full(self):
        return self.call_wrapper(self.executer.is_queue_full)

    def wait(self):
        return self.call_wrapper(self.executer.wait)

def get_platform_name():
    from infi.os_info import get_platform_string
    return get_platform_string().split('-')[0]

def create_platform_command_executer(*args, **kwargs):
    platform_name = get_platform_name()
    CommandExecuterForPlatform = None
    if platform_name == 'windows':
        from .win32 import Win32CommandExecuter as CommandExecuterForPlatform
    elif platform_name == 'linux':
        from .linux import LinuxCommandExecuter as CommandExecuterForPlatform
    elif platform_name == 'solaris':
        from .solaris import SolarisCommandExecuter as CommandExecuterForPlatform
    elif platform_name == 'aix':
        from .aix import AixCommandExecuter as CommandExecuterForPlatform
    else:
        raise AsiException("Platform %s is not yet supported." % platform_name)
    return CommandExecuterForPlatform(*args, **kwargs)

def create_os_file(path):
    platform_name = get_platform_name()
    if platform_name == 'windows':
        from .win32 import Win32File
        return Win32File(path)
    elif platform_name in ['linux', 'aix']:
        from .unix import UnixFile
        return UnixFile(os.open(path, os.O_RDWR))
    elif platform_name == 'solaris':
        from .unix import UnixFile
        return UnixFile(os.open(path, os.O_RDWR|os.O_NONBLOCK))
    raise AsiException("Platform %s is not yet supported." % platform_name)

def create_async_os_file(path):
    platform_name = get_platform_name()
    if platform_name == 'windows':
        from .win32 import Win32AsyncFile
        return Win32AsyncFile(path)
    raise AsiException("Platform %s is not yet supported." % platform_name)

def create_os_async_reactor():
    platform_name = get_platform_name()
    if platform_name == 'windows':
        from .win32 import Win32AsyncReactor
        return Win32AsyncReactor()
    raise AsiException("Platform %s is not yet supported." % platform_name)


def gevent_friendly(func):
    """asi sends IOCTLs which are blocking and not gevent-friendly
    if gevent is being used, we would like to give other greenlets a chance to run after IO
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return_value = func(*args, **kwargs)
        _gevent_friendly_sleep(0)
        return return_value
    return wrapper
