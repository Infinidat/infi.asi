import os
from infi.asi import win32
from infi.asi.cdb.inquiry.standard import StandardInquiryCommand
from infi.exceptools import print_exc
from ctypes import *
from binascii import hexlify
import six

DeviceIoControl = windll.kernel32.DeviceIoControl
GetLastError = windll.kernel32.GetLastError
FormatMessage = windll.kernel32.FormatMessageA

def errno_message(errno):
    buf = create_string_buffer(1024)
    FormatMessage(0x00001000, 0, errno & 0xFFFF, 0, buf, sizeof(buf), 0)
    return buf.value.strip()

SENSE_SIZE = 0x12

IOCTL_SCSI_PASS_THROUGH_DIRECT = 0x0004D014

SCSI_IOCTL_DATA_OUT         = 0 # Write data to the device
SCSI_IOCTL_DATA_IN          = 1 # Read data from the device
SCSI_IOCTL_DATA_UNSPECIFIED = 2 # No data is transferred

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

        # sizeof: 16 + 4 + 8 + 4 + 4 + 1 * 7 + 2 =
        # Our sense buffer
        ("sense_buffer", c_ubyte * SENSE_SIZE)
   ]

try:
    cmd = StandardInquiryCommand()
    cmd_str = cmd.create_datagram()

    f = win32.Win32File(r"\\.\PHYSICALDRIVE0",
               win32.GENERIC_READ | win32.GENERIC_WRITE,
               win32.FILE_SHARE_READ | win32.FILE_SHARE_WRITE,
               win32.OPEN_EXISTING)

    data_buffer = create_string_buffer(96)
    print("[!] SPT length: %d (%d)" % (sizeof(SCSIPassThroughDirect) - SENSE_SIZE, sizeof(SCSIPassThroughDirect)))
    spt = SCSIPassThroughDirect()
    spt.Length = sizeof(SCSIPassThroughDirect) - SENSE_SIZE
    spt.PathId = 0
    spt.TargetId = 0
    spt.Lun = 0
    spt.CdbLength = StandardInquiryCommand.sizeof(cmd)
    spt.SenseInfoLength = SENSE_SIZE
    spt.DataIn = SCSI_IOCTL_DATA_IN
    spt.DataTransferLength = sizeof(data_buffer)
    spt.TimeOutValue = 10
    spt.DataBuffer = cast(data_buffer, c_void_p)
    spt.SenseInfoOffset = sizeof(SCSIPassThroughDirect) - SENSE_SIZE
    for i in range(len(cmd_str)):
        spt.Cdb[i] = six.indexbytes(cmd_str, i)  # ord(cmd_str[i])

    bytes_returned = c_ulong()
    print("SCSI status before: %x" % spt.ScsiStatus)
    if not DeviceIoControl(f.handle, IOCTL_SCSI_PASS_THROUGH_DIRECT, byref(spt), sizeof(spt),
                           byref(spt), sizeof(spt),
                           byref(bytes_returned), None):
        raise IOError("DeviceIoControl failed [errno=%d, errmsg=%s]" % (GetLastError(), errno_message(GetLastError())))
    print("SCSI status after: %x" % spt.ScsiStatus)
    print("DataTransferLength: %d" % (spt.DataTransferLength,))
    print("bytes_returned: %d" % (bytes_returned.value,))
    print("data buffer: %s (%s)" % (hexlify(data_buffer.raw), data_buffer.raw))
    print("Sense buffer: %s" % hexlify(spt.sense_buffer))
except:
    print_exc()
