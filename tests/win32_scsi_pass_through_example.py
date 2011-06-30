import os
from infi.asi.win32 import OSFile
from infi.asi.cdb.inquiry import StandardInquiryData, StandardInquiryCommand
from infi.exceptools import print_exc
from ctypes import *

DeviceIoControl = windll.kernel32.DeviceIoControl
GetLastError = windll.kernel32.GetLastError
FormatMessage = windll.kernel32.FormatMessageA

def errno_message(errno):
    buf = create_string_buffer(1024)
    FormatMessage(0x00001000, 0, errno & 0xFFFF, 0, buf, sizeof(buf), 0)
    return buf.value.strip()

SENSE_SIZE = 0xFF

IOCTL_SCSI_PASS_THROUGH_DIRECT = 0x0004D014L

SCSI_IOCTL_DATA_OUT         = 0 # Write data to the device 
SCSI_IOCTL_DATA_IN          = 1 # Read data from the device
SCSI_IOCTL_DATA_UNSPECIFIED = 2 # No data is transferred

class SCSIPassThroughDirect(Structure):
#     _pack_ = 8
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
        ("padding1", c_ubyte * 3),
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
    cmd = StandardInquiryCommand.create()
    cmd_str = StandardInquiryCommand.instance_to_string(cmd)
    
    f = OSFile(r"\\.\PHYSICALDRIVE0",
               OSFile.GENERIC_READ | OSFile.GENERIC_WRITE,
               OSFile.FILE_SHARE_READ | OSFile.FILE_SHARE_WRITE,
               OSFile.OPEN_EXISTING)

    data_buffer = create_string_buffer(96)

    print("SPT length: %d" % (sizeof(SCSIPassThroughDirect) - SENSE_SIZE))
    spt = SCSIPassThroughDirect()
    spt.Length = sizeof(SCSIPassThroughDirect) - SENSE_SIZE
    spt.PathId = 0
    spt.TargetId = 0
    spt.Lun = 0
    spt.CdbLength = StandardInquiryCommand.sizeof()
    spt.SenseInfoLength = SENSE_SIZE
    spt.DataIn = SCSI_IOCTL_DATA_IN
    spt.DataTransferLength = sizeof(data_buffer)
    spt.TimeOutValue = 10
    spt.DataBuffer = cast(data_buffer, c_void_p)
    spt.SenseInfoOffset = sizeof(SCSIPassThroughDirect) - SENSE_SIZE
    for i in xrange(len(cmd_str)):
        spt.Cdb[i] = ord(cmd_str[i])

    bytes_returned = c_ulong()
    if not DeviceIoControl(f.handle, IOCTL_SCSI_PASS_THROUGH_DIRECT, byref(spt), sizeof(spt), 0, 0, byref(bytes_returned), 0):
        raise IOError("DeviceIoControl failed [errno=%d, errmsg=%s]" % (GetLastError(), errno_message(GetLastError())))
except:
    print_exc()
