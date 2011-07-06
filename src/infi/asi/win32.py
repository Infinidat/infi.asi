from ctypes import *
from . import CommandExecuterBase, DEFAULT_MAX_QUEUE_SIZE, SCSIReadCommand, SCSIWriteCommand
from .errors import AsiOSError

class AsiWin32OSError(AsiOSError):
    def __init__(self, errno, details=None):
        buf = ctypes.create_string_buffer(1024)
        FormatMessage(0x00001000, 0, errno & 0xFFFF, 0, buf, sizeof(buf), 0)
        error_string = buf.value.strip()
        
        if details is not None:
            message = "%s (win32 error %d: %s)" % (details, errno, error_string)
        else:
            message = "Win32 error %d: %s" % (errno, error_string)
        super(AsiWin32OSError, self).__init__(error_string)
        self.win32_errno = errno
        self.win32_message = error_string

kernel32 = windll.kernel32

"""
DWORD WINAPI GetLastError(void);
"""
GetLastError = kernel32.GetLastError

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
CreateFile = kernel32.CreateFileA

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

class OSFile(object):
    GENERIC_READ    = 0x80000000L
    GENERIC_WRITE   = 0x40000000L
    GENERIC_EXECUTE = 0x20000000L
    GENERIC_ALL     = 0x10000000L
    
    FILE_SHARE_READ   = 0x00000001
    FILE_SHARE_WRITE  = 0x00000002
    FILE_SHARE_NONE   = 0x00000000
    FILE_SHARE_DELETE = 0x00000004

    CREATE_NEW        = 1
    CREATE_ALWAYS     = 2
    OPEN_EXISTING     = 3
    OPEN_ALWAYS       = 4
    TRUNCATE_EXISTING = 5

    FILE_FLAG_OVERLAPPED = 0x40000000L
    
    def __init__(self, path, access, share, creation_disposition, flags=0):
        self.path = path
        self.handle = CreateFile(path, access, share, 0, creation_disposition, flags, 0)
        if self.handle == -1:
            raise AsiWin32OSError(GetLastError(), "CreateFile for path %s failed" % path)

    def close(self):
        if self.handle == -1:
            return
        if not CloseHandle(self.handle):
            raise AsiWin32OSError(GetLastError(), "CloseHandle for path %s failed" % self.path)
        self.handle = -1

    def ioctl(control_code, input, input_size, output=None, output_size=0):
        bytes_returned = c_ulong(0)
        if not DeviceIoControl(self.handle, control_code, input, input_size, output or 0, output_size,
                               byref(bytes_returned), 0):
            raise AsiWin32OSError(GetLastError(), "DeviceIoControl %d for path %s failed" % (control_code, self.path))
        return bytes_returned.value

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
IOCTL_SCSI_PASS_THROUGH_DIRECT = 0x0004D014L

SCSI_IOCTL_DATA_OUT         = 0 # Write data to the device 
SCSI_IOCTL_DATA_IN          = 1 # Read data from the device
SCSI_IOCTL_DATA_UNSPECIFIED = 2 # No data is transferred

SENSE_SIZE = 0xFF

class SCSIPassThroughDirect(Structure):
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
        ("DataBuffer", c_void_p),
        # [in] Offset from the beginning of the structure to the request-sense buffer
        ("SenseInfoOffset", c_ulong),
        # [in] CDB to send to the target device
        ("Cdb", c_ubyte * 16),

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
    def create(cls, packet_index, command):
        buf = create_string_buffer(sizeof(SCSIPassThroughDirect))
        spt = SCSIPassThroughDirect.from_buffer(buf)
        spt.source_buffer = buf
        spt.packet_index = packet_index
        spt.Length = sizeof(SCSIPassThroughDirect) - SENSE_SIZE
        spt.PathId = 0
        spt.TargetId = 0
        spt.Lun = 0
        spt.CdbLength = StandardInquiryCommand.sizeof()
        spt.SenseInfoLength = SENSE_SIZE
        spt.TimeOutValue = 10 # TODO: configurable
        spt.SenseInfoOffset = sizeof(SCSIPassThroughDirect) - SENSE_SIZE
        for i in xrange(len(command.command)):
            spt.Cdb[i] = ord(command.command[i])

        if isinstance(command, SCSIReadCommand):
            if command.max_response_length > 0:
                spt.DataIn = SCSI_IOCTL_DATA_IN
                spt.set_data_buffer(create_string_buffer(command.max_response_length))
            else:
                spt.dxfer_direction = SCSI_IOCTL_DATA_UNSPECIFIED
                spt.set_data_buffer(None)
        else:
            sgio.dxfer_direction = SCSI_IOCTL_DATA_OUT
            sgio.set_data_buffer(create_string_buffer(command.data, len(command.data)))

class Win32CommandExecuter(CommandExecuter):
    def __init__(self, io, max_queue_size=DEFAULT_MAX_QUEUE_SIZE):
        super(Win32CommandExecuter, self).__init__(max_queue_size)
        self.io = io
        self.incoming_packets = []

    def _os_prepare_to_send(self, command, packet_index):
        return SCSIPassThroughDirect.create(packet_index, command)

    def _os_send(self, os_data):
        yield self.io.ioctl(IOCTL_SCSI_PASS_THROUGH_DIRECT,
                            byref(os_data.source_buffer), sizeof(SCSIPassThroughDirect),
                            byref(os_data.source_buffer), sizeof(SCSIPassThroughDirect))
        self.incoming_packets.append(os_data)
        
    def _os_receive(self):
        spt = self.incoming_packets.pop()
        if spt.ScsiStatus != 0:
            # TODO: check sense buffer.
            yield (AsiSCSIError("SCSI response status is not zero: %d" % (spt.ScsiStatus,)), spt.packet_id)

        data = None
        if spt.DataIn == SCSI_IOCTL_DATA_IN and spt.DataTransferLength != 0:
            data = spt.data_buffer.raw[0:spt.DataTransferLength]

        yield (data, packet_id)