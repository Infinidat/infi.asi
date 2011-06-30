from ctypes import *
from . import CommandExecuter, SCSIReadCommand, SCSIWriteCommand

kernel32 = windll.kernel32

"""
DWORD WINAPI GetLastError(void);
"""
GetLastError = kernel32.GetLastError

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

def errno_message(errno):
    buf = ctypes.create_string_buffer(1024)
    FormatMessage(0x00001000, 0, errno & 0xFFFF, 0, buf, sizeof(buf), 0)
    return buf.value.strip()

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
        self.handle = CreateFile(path, access, share, 0, creation_disposition, flags, 0)
        if self.handle == -1:
            raise self._io_error("CreateFile failed")

    def close(self):
        if self.handle == -1:
            return
        if not CloseHandle(self.handle):
            raise self._io_error("CloseHandle failed")

    def ioctl(control_code, input, output_size):
        output = create_string_buffer(output_size)
        bytes_returned = c_ulong(0)
        if not DeviceIoControl(self.handle, control_code, input, len(input), output, output_size, byref(bytes_returned),
                               0):
            raise self._io_error("DeviceIoControl failed")
        return output.raw[0:bytes_returned.value]

    def _io_error(self, message):
        errno = GetLastError()
        return IOError("%s [errno=%d, message=%d]" % (message, errno_message(errno)))



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
    
DEFAULT_MAX_QUEUE_SIZE = 15

class Win32CommandExecuter(CommandExecuter):
    def __init__(self, io, max_queue_size=DEFAULT_MAX_QUEUE_SIZE):
        super(CommandExecuter, self).__init__()
        self.io = io
        self.pending_packets = dict()
        self.max_queue_size = max_queue_size
        self.packet_index = 0

    def _next_packet_index(self):
        if len(self.pending_packets) >= self.max_queue_size:
            # TODO: exceptions
            raise Exception("Too many packets are already pending.")
        result = self.packet_index
        self.packet_index = (self.packet_index + 1) % self.max_queue_size
        return result
    
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
        
        sgio = SGIO.create(packet_index, command)
        
        self.pending_packets[packet_index] = (sgio, callback)
        
        yield self.io.write(sgio.to_raw())

    def wait(self):
        while not self.is_queue_empty():
            yield self._process_pending_response()

    def _process_pending_response(self):
        if self.is_queue_empty():
            yield False

        raw = yield self.io.read(sizeof(SGIO))
        
        response_sgio = SGIO.from_string(raw)

        request_sgio, callback = self.pending_packets.pop(response_sgio.pack_id, (None, None))
        if request_sgio is None:
            # TODO: exceptions
            raise Exception("Response doesn't appear in the pending I/O list.")

        # TODO: check for errors.
        exception = None
        if response_sgio.status != 0:
            exception = Exception("Response status is not zero.")
            
        data = None
        if request_sgio.dxfer_direction == SG_DXFER_FROM_DEV and request_sgio.dxfer_len != 0:
            data = request_sgio.data_buffer.raw
            
        if callback is not None:
            callback(data, exception)
        
        yield True
