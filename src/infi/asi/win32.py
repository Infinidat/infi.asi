from ctypes import *
from . import CommandExecuterBase, DEFAULT_MAX_QUEUE_SIZE, SCSIReadCommand, SCSIWriteCommand
from .errors import AsiOSError, AsiSCSIError
from . import OSAsyncIOToken, OSFile, OSAsyncFile, OSAsyncReactor, DEFAULT_TIMEOUT, gevent_friendly
from .coroutines.sync_adapter import AsyncCoroutine
import six

# Taken from Windows DDK
# WinDDK/7600.16385.1/inc/ddk/scsi.h
SCSISTAT_GOOD                   = 0x00
SCSISTAT_CHECK_CONDITION        = 0x02
SCSISTAT_CONDITION_MET          = 0x04
SCSISTAT_BUSY                   = 0x08
SCSISTAT_INTERMEDIATE           = 0x10
SCSISTAT_INTERMEDIATE_COND_MET  = 0x14
CSISTAT_RESERVATION_CONFLICT    = 0x18
SCSISTAT_COMMAND_TERMINATED     = 0x22
SCSISTAT_QUEUE_FULL             = 0x28

class AsiWin32OSError(AsiOSError):
    def __init__(self, errno, details=None):
        buf = create_string_buffer(1024)
        FormatMessage(0x00001000, 0, errno & 0xFFFF, 0, buf, sizeof(buf), 0)
        error_string = buf.value.strip()

        if details is not None:
            message = "%s (win32 error %d: %s)" % (details, errno, error_string)
        else:
            message = "Win32 error %d: %s" % (errno, error_string)
        super(AsiWin32OSError, self).__init__(message)
        self.win32_errno = errno
        self.win32_message = error_string

kernel32 = windll.kernel32

"""
DWORD WINAPI GetLastError(void);
"""
GetLastError = kernel32.GetLastError

ERROR_IO_PENDING = 997

"""
DWORD WINAPI FormatMessage(
  __in      DWORD dwFlags,
  __in_opt  LPCVOID lpSource,
  __in      DWORD dwMessageId,
  __in      DWORD dwLanguageId,
  __out     LPTSTR lpBuffer,
  __in      DWORD nSize,
  __in_opt  va_list *Arguments
);
"""
FormatMessage = kernel32.FormatMessageA

"""
HANDLE WINAPI CreateFile(
  __in      LPCTSTR lpFileName,
  __in      DWORD dwDesiredAccess,
  __in      DWORD dwShareMode,
  __in_opt  LPSECURITY_ATTRIBUTES lpSecurityAttributes,
  __in      DWORD dwCreationDisposition,
  __in      DWORD dwFlagsAndAttributes,
  __in_opt  HANDLE hTemplateFile
);
"""
CreateFile = kernel32.CreateFileW

"""
BOOL WINAPI DeviceIoControl(
  __in         HANDLE hDevice,
  __in         DWORD dwIoControlCode,
  __in_opt     LPVOID lpInBuffer,
  __in         DWORD nInBufferSize,
  __out_opt    LPVOID lpOutBuffer,
  __in         DWORD nOutBufferSize,
  __out_opt    LPDWORD lpBytesReturned,
  __inout_opt  LPOVERLAPPED lpOverlapped
);
"""
DeviceIoControl = kernel32.DeviceIoControl

"""
BOOL WINAPI CloseHandle(
  __in  HANDLE hObject
);
"""
CloseHandle = kernel32.CloseHandle

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
GENERIC_EXECUTE = 0x20000000
GENERIC_ALL = 0x10000000

FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_NONE = 0x00000000
FILE_SHARE_DELETE = 0x00000004

CREATE_NEW = 1
CREATE_ALWAYS = 2
OPEN_EXISTING = 3
OPEN_ALWAYS = 4
TRUNCATE_EXISTING = 5

FILE_FLAG_OVERLAPPED = 0x40000000

IOCTL_ACCESS = GENERIC_READ | GENERIC_WRITE
IOCTL_SHARE = FILE_SHARE_READ | FILE_SHARE_WRITE
IOCTL_CREATION = OPEN_EXISTING

class Win32File(OSFile):

    def __init__(self, path, access=IOCTL_ACCESS, share=IOCTL_SHARE,
                 creation_disposition=IOCTL_CREATION, flags=0):
        import six
        self.path = six.text_type(path)
        self.handle = CreateFile(self.path, access, share, None, creation_disposition, flags, None)
        if self.handle == -1:
            raise AsiWin32OSError(GetLastError(), "CreateFile for path %s failed" % path)

    def close(self):
        if self.handle == -1:
            return
        if not CloseHandle(c_void_p(self.handle)):
            raise AsiWin32OSError(GetLastError(), "CloseHandle for path %s failed" % self.path)
        self.handle = -1

    def ioctl(self, control_code, input, input_size, output=None, output_size=0):
        bytes_returned = c_ulong(0)
        if not DeviceIoControl(c_void_p(self.handle), control_code, input, input_size, output or None, output_size,
                               byref(bytes_returned), None):
            raise AsiWin32OSError(GetLastError(), "DeviceIoControl %d for path %s failed" % (control_code, self.path))
        return bytes_returned.value

def overlapped_struct_from_event(event):
    from struct import pack
    return c_buffer(pack("PPLLP", 0, 0, 0, 0, event))

class WinAsyncIOToken(OSAsyncIOToken):
    def __init__(self, file_handle, overlapped_struct, event_handle):
        self.handle = file_handle
        self.event = event_handle
        self.overlapped = overlapped_struct

    def get_result(self, block=False):
        result = c_ulong()
        overlapped_struct = overlapped_struct_from_event(self.event)
        err = kernel32.GetOverlappedResult(self.handle, byref(self.overlapped), byref(result), block)
        return result

class Win32AsyncFile(OSAsyncFile, Win32File):
    def __init__(self, path, access=IOCTL_ACCESS, share=IOCTL_SHARE,
                 creation_disposition=IOCTL_CREATION, flags=0):
        flags |= FILE_FLAG_OVERLAPPED
        super(Win32AsyncFile, self).__init__(path, access, share, creation_disposition, flags)

    def _create_overlapped_struct(self):
        self._windows_event_handle = kernel32.CreateEventW(None, True, False, None)
        self._overlapped_struct = overlapped_struct_from_event(self._windows_event_handle)

    def ioctl(self, control_code, input, input_size, output=None, output_size=0):
        self._create_overlapped_struct()
        api_result = DeviceIoControl(self.handle, control_code, input, input_size, output, output_size,
                                     None, byref(self._overlapped_struct))
        last_error = GetLastError()
        if not api_result and last_error == ERROR_IO_PENDING:
            token = WinAsyncIOToken(self.handle, self._overlapped_struct, self._windows_event_handle)
            yield token
        else:
            raise AsiWin32OSError(GetLastError(), "DeviceIoControl %d for path %s failed" % (control_code, self.path))

def WaitForMultipleObjects(events):
    from struct import pack
    event_array = pack("{}P".format(len(events)), *events)
    result = kernel32.WaitForMultipleObjects(len(events), byref(c_buffer(event_array)), False, DEFAULT_TIMEOUT)
    if result < 0 or result >= 128:
        raise AsiWin32OSError(GetLastError(), "WaitForMultipleObjects failed. result={}".format(result))
    return result

class Win32AsyncReactor(OSAsyncReactor):
    def _wait_for_events(self, coroutines):
        events = {coroutine.get_result().event: (command, coroutine) for (command, coroutine) in coroutines.items()}
        returned_event_index = WaitForMultipleObjects(list(events.keys()))
        returned_event = list(events.keys())[returned_event_index]
        command, coroutine = events[returned_event]
        coroutine.async_io_complete()
        return [command]

    def wait_for(self, *commands):
        coroutines = {command: AsyncCoroutine(command) for command in commands}
        non_blocking_commands = commands[:]
        results_dict = {}

        while len(coroutines) > 0:
            for command in non_blocking_commands:
                coroutine = coroutines[command]
                coroutine.loop()
                if coroutine.is_done():
                    results_dict[command] = coroutine.get_result()
                    del coroutines[command]
            if len(coroutines) > 0:
                non_blocking_commands = self._wait_for_events(coroutines)

        # sort results_dict in the same order as commands
        results = []
        for command in commands:
            results.append(results_dict[command])
        return results

"""
Defined in the Windows DDK, under inc/api/ntddscsi.h

typedef struct _SCSI_PASS_THROUGH {
    USHORT Length;
    UCHAR ScsiStatus;
    UCHAR PathId;
    UCHAR TargetId;
    UCHAR Lun;
    UCHAR CdbLength;
    UCHAR SenseInfoLength;
    UCHAR DataIn;
    ULONG DataTransferLength;
    ULONG TimeOutValue;
    ULONG_PTR DataBufferOffset;
    ULONG SenseInfoOffset;
    UCHAR Cdb[16];
}SCSI_PASS_THROUGH, *PSCSI_PASS_THROUGH;

typedef struct _SCSI_PASS_THROUGH_DIRECT {
    USHORT Length;
    UCHAR ScsiStatus;
    UCHAR PathId;
    UCHAR TargetId;
    UCHAR Lun;
    UCHAR CdbLength;
    UCHAR SenseInfoLength;
    UCHAR DataIn;
    ULONG DataTransferLength;
    ULONG TimeOutValue;

    PVOID DataBuffer;
    ULONG SenseInfoOffset;
    UCHAR Cdb[16];
}SCSI_PASS_THROUGH_DIRECT, *PSCSI_PASS_THROUGH_DIRECT;

#define SCSI_IOCTL_DATA_OUT          0
#define SCSI_IOCTL_DATA_IN           1
#define SCSI_IOCTL_DATA_UNSPECIFIED  2

#define IOCTL_SCSI_BASE FILE_DEVICE_CONTROLLER
#define IOCTL_SCSI_PASS_THROUGH CTL_CODE(IOCTL_SCSI_BASE, 0x0401, METHOD_BUFFERED, FILE_READ_ACCESS | FILE_WRITE_ACCESS)
#define IOCTL_SCSI_PASS_THROUGH_DIRECT CTL_CODE(IOCTL_SCSI_BASE, 0x0405, METHOD_BUFFERED, FILE_READ_ACCESS | FILE_WRITE_ACCESS)

// devioctl.h and winioctl.h:
#define FILE_DEVICE_CONTROLLER          0x00000004
#define FILE_READ_ACCESS          ( 0x0001 )    // file & pipe
#define FILE_WRITE_ACCESS         ( 0x0002 )    // file & pipe
#define CTL_CODE( DeviceType, Function, Method, Access ) (                 \
    ((DeviceType) << 16) | ((Access) << 14) | ((Function) << 2) | (Method) \

// So, IOCTL_SCSI_PASS_THROUGH_DIRECT is:
// (IOCTL_SCSI_BASE << 16) | (0x0001 | 0x0002) << 14 | (0x0405 << 2) | 0 = 0x0004D014
"""
IOCTL_SCSI_PASS_THROUGH_DIRECT = 0x0004D014

SCSI_IOCTL_DATA_OUT = 0 # Write data to the device
SCSI_IOCTL_DATA_IN = 1 # Read data from the device
SCSI_IOCTL_DATA_UNSPECIFIED = 2 # No data is transferred

SENSE_SIZE = 0xFF

def is_python_64bit():
    from sys import maxsize
    return maxsize > 2 ** 32

class SCSIPassThroughDirect(Structure):
    _pack_ = 1
    _fields_ = [
        # [in] sizeof(SCSI_PASS_THROUGH)
        ("Length", c_ushort),
        # [out] SCSI status returned by the HBA/target device
        ("ScsiStatus", c_ubyte),
        # [in] SCSI port or bus for the request
        ("PathId", c_ubyte),
        # [in] Target controller or device on the bus
        ("TargetId", c_ubyte),
        # [in] Logical unit number of the device
        ("Lun", c_ubyte),
        # [in] Size in bytes of the SCSI CDB
        ("CdbLength", c_ubyte),
        # [in] Size in bytes of the request-sense buffer
        ("SenseInfoLength", c_ubyte),
        # [in] One of: SCSI_IOCTL_DATA_IN, SCSI_IOCTL_DATA_OUT, SCSI_IOCTL_DATA_UNSPECIFIED
        ("DataIn", c_ubyte),
        # TODO: This is only for 32bit python, we need this for 64 bit as well.
        ("padding1", c_ubyte * 3),
        # [in/out] Size in bytes of the data buffer
        ("DataTransferLength", c_ulong),
        # [in] Interval in seconds
        ("TimeOutValue", c_ulong),
        # [in] Pointer to the data buffer
        ("padding2", c_ubyte * (4 if is_python_64bit() else 0)),
        ("DataBuffer", c_void_p),
        # [in] Offset from the beginning of the structure to the request-sense buffer
        ("SenseInfoOffset", c_ulong),
        # [in] CDB to send to the target device
        ("Cdb", c_ubyte * 16),
        ("padding3", c_ubyte * (4 if is_python_64bit() else 0)),

        # Our sense buffer
        ("sense_buffer", c_ubyte * SENSE_SIZE)
    ]

    def set_data_buffer(self, buf):
        if buf is not None:
            self.data_buffer = buf
            self.DataBuffer = cast(self.data_buffer, c_void_p)
            self.DataTransferLength = sizeof(self.data_buffer)
        else:
            self.DataTransferLength = 0
            self.DataBuffer = 0

    def to_raw(self):
        return self.source_buffer.raw

    @classmethod
    def create(cls, packet_id, command):
        buf = create_string_buffer(sizeof(SCSIPassThroughDirect))
        spt = SCSIPassThroughDirect.from_buffer(buf)
        spt.source_buffer = buf
        spt.packet_id = packet_id
        spt.Length = sizeof(SCSIPassThroughDirect) - SENSE_SIZE
        spt.PathId = 0
        spt.TargetId = 0
        spt.Lun = 0
        spt.CdbLength = len(command.command)
        spt.SenseInfoLength = SENSE_SIZE
        spt.TimeOutValue = 10 # TODO: configurable
        spt.SenseInfoOffset = sizeof(SCSIPassThroughDirect) - SENSE_SIZE
        for i in range(len(command.command)):
            spt.Cdb[i] = six.indexbytes(command.command, i)  # ord(command.command[i])

        if isinstance(command, SCSIReadCommand):
            if command.max_response_length > 0:
                spt.DataIn = SCSI_IOCTL_DATA_IN
                spt.set_data_buffer(create_string_buffer(command.max_response_length))
            else:
                spt.DataIn = SCSI_IOCTL_DATA_UNSPECIFIED
                spt.set_data_buffer(None)
        else:
            if len(command.data) > 0:
                spt.DataIn = SCSI_IOCTL_DATA_OUT
                spt.set_data_buffer(create_string_buffer(command.data, len(command.data)))
            else:
                spt.DataIn = SCSI_IOCTL_DATA_UNSPECIFIED

        return spt

class Win32CommandExecuter(CommandExecuterBase):
    def __init__(self, io, max_queue_size=DEFAULT_MAX_QUEUE_SIZE):
        super(Win32CommandExecuter, self).__init__(max_queue_size)
        self.io = io
        self.incoming_packets = []

    def _os_prepare_to_send(self, command, packet_id):
        return SCSIPassThroughDirect.create(packet_id, command)

    def _os_send(self, os_data):
        yield gevent_friendly(self.io.ioctl)(IOCTL_SCSI_PASS_THROUGH_DIRECT,
                                            byref(os_data.source_buffer), sizeof(SCSIPassThroughDirect),
                                            byref(os_data.source_buffer), sizeof(SCSIPassThroughDirect))
        self.incoming_packets.append(os_data)

    def _os_receive(self):
        spt = self.incoming_packets.pop()
        if spt.ScsiStatus != 0:
            if spt.ScsiStatus == SCSISTAT_CHECK_CONDITION:
                yield (self._check_condition(string_at(spt.sense_buffer, SENSE_SIZE)), spt.packet_id)
                return
            yield (AsiSCSIError("SCSI response status is not zero: %d" % (spt.ScsiStatus,)), spt.packet_id)
            return
        data = None
        if spt.DataIn == SCSI_IOCTL_DATA_IN and spt.DataTransferLength != 0:
            data = spt.data_buffer.raw[0:spt.DataTransferLength]

        yield (data, spt.packet_id)

# backward compatibility
OSFile = Win32File
