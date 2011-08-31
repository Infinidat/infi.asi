from . import CommandExecuterBase, DEFAULT_MAX_QUEUE_SIZE, SCSIReadCommand, SCSIWriteCommand
from . import SCSI_STATUS_CHECK_CONDITION
from .errors import AsiSCSIError
from ctypes import *

"""
From /usr/include/scsi/sg.h

See http://tldp.org/HOWTO/SCSI-Generic-HOWTO/sg_io_hdr_t.html

typedef struct sg_io_hdr
{
  int interface_id;           /* [i] 'S' for SCSI generic (required) */
  int dxfer_direction;        /* [i] data transfer direction  */
  unsigned char cmd_len;      /* [i] SCSI command length ( <= 16 bytes) */
  unsigned char mx_sb_len;    /* [i] max length to write to sbp */
  unsigned short int iovec_count; /* [i] 0 implies no scatter gather */
  unsigned int dxfer_len;     /* [i] byte count of data transfer */
  void * dxferp;              /* [i], [*io] points to data transfer memory
				 or scatter gather list */
  unsigned char * cmdp;       /* [i], [*i] points to command to perform */
  unsigned char * sbp;        /* [i], [*o] points to sense_buffer memory */
  unsigned int timeout;       /* [i] MAX_UINT->no timeout (unit: millisec) */
  unsigned int flags;         /* [i] 0 -> default, see SG_FLAG... */
  int pack_id;                /* [i->o] unused internally (normally) */
  void * usr_ptr;             /* [i->o] unused internally */
  unsigned char status;       /* [o] scsi status */
  unsigned char masked_status;/* [o] shifted, masked scsi status */
  unsigned char msg_status;   /* [o] messaging level data (optional) */
  unsigned char sb_len_wr;    /* [o] byte count actually written to sbp */
  unsigned short int host_status; /* [o] errors from host adapter */
  unsigned short int driver_status;/* [o] errors from software driver */
  int resid;                  /* [o] dxfer_len - actual_transferred */
  unsigned int duration;      /* [o] time taken by cmd (unit: millisec) */
  unsigned int info;          /* [o] auxiliary information */
} sg_io_hdr_t;

#define SG_DXFER_NONE -1        /* e.g. a SCSI Test Unit Ready command */
#define SG_DXFER_TO_DEV -2      /* e.g. a SCSI WRITE command */
#define SG_DXFER_FROM_DEV -3    /* e.g. a SCSI READ command */
#define SG_DXFER_TO_FROM_DEV -4 /* treated like SG_DXFER_FROM_DEV with the
				   additional property than during indirect
				   IO the user buffer is copied into the
				   kernel buffers before the transfer */


/* following flag values can be "or"-ed together */
#define SG_FLAG_DIRECT_IO 1     /* default is indirect IO */
#define SG_FLAG_LUN_INHIBIT 2   /* default is to put device's lun into */
				/* the 2nd byte of SCSI command */
#define SG_FLAG_NO_DXFER 0x10000 /* no transfer of kernel buffers to/from */
				/* user space (debug indirect IO) */

/* The following 'info' values are "or"-ed together.  */
#define SG_INFO_OK_MASK	0x1
#define SG_INFO_OK	0x0	/* no sense, host nor driver "noise" */
#define SG_INFO_CHECK	0x1     /* something abnormal happened */

#define SG_INFO_DIRECT_IO_MASK	0x6
#define SG_INFO_INDIRECT_IO 	0x0	/* data xfer via kernel buffers (or no xfer) */
#define SG_INFO_DIRECT_IO 	0x2	/* direct IO requested and performed */
#define SG_INFO_MIXED_IO 	0x4	/* part direct, part indirect IO */
"""
SG_DXFER_NONE = -1
SG_DXFER_TO_DEV = -2
SG_DXFER_FROM_DEV = -3
SG_DXFER_TO_FROM_DEV = -4
SG_FLAG_DIRECT_IO = 1
SG_FLAG_LUN_INHIBIT = 2
SG_FLAG_NO_DXFER = 0x10000

SENSE_SIZE = 0xFF

class SGIO(Structure):
    _fields_ = [
        ("interface_id", c_int),
        ("dxfer_direction", c_int),
        ("cmd_len", c_ubyte),
        ("mx_sb_len", c_ubyte),
        ("iovec_count", c_ushort),
        ("dxfer_len", c_uint),
        ("dxferp", c_void_p),
        ("cmdp", c_void_p),
        ("sbp", c_void_p),
        ("timeout", c_uint),
        ("flags", c_uint),
        ("pack_id", c_int),
        ("usr_ptr", c_void_p),
        ("status", c_ubyte),
        ("masked_status", c_ubyte),
        ("msg_status", c_ubyte),
        ("sb_len_wr", c_ubyte),
        ("host_status", c_ushort),
        ("driver_status", c_ushort),
        ("resid", c_int),
        ("duration", c_uint),
        ("info", c_uint)
    ]

    def __init__(self, *args, **kwargs):
        super(SGIO, self).__init__(*args, **kwargs)
        self.source_buffer = None

    def init_sense_buffer(self):
        self.sense_buffer = create_string_buffer(SENSE_SIZE)
        self.sbp = cast(self.sense_buffer, c_void_p)
        self.mx_sb_len = sizeof(self.sense_buffer)

    def init_command_buffer(self, command):
        self.command_buffer = create_string_buffer(command, len(command))
        self.cmdp = cast(self.command_buffer, c_void_p)
        self.cmd_len = sizeof(self.command_buffer)
        
    def set_data_buffer(self, buf):
        if buf is not None:
            self.data_buffer = buf
            self.dxferp = cast(self.data_buffer, c_void_p)
            self.dxfer_len = sizeof(self.data_buffer)
        else:
            self.dxfer_len = 0
            self.dxferp = 0
            
    def to_raw(self):
        return self.source_buffer.raw

    @classmethod
    def create(cls, pack_id, command):
        buf = create_string_buffer(sizeof(SGIO))
        sgio = SGIO.from_buffer(buf)
        sgio.source_buffer = buf
        sgio.interface_id = ord('S')
        sgio.pack_id = pack_id
        sgio.init_sense_buffer()
        sgio.init_command_buffer(command.command)

        if isinstance(command, SCSIReadCommand):
            if command.max_response_length > 0:
                sgio.dxfer_direction = SG_DXFER_FROM_DEV
                sgio.set_data_buffer(create_string_buffer(command.max_response_length))
            else:
                sgio.dxfer_direction = SG_DXFER_NONE
                sgio.set_data_buffer(None)
        else:
            sgio.dxfer_direction = SG_DXFER_TO_DEV
            sgio.set_data_buffer(create_string_buffer(command.data, len(command.data)))

        sgio.flags = SG_FLAG_DIRECT_IO
        return sgio

    @classmethod
    def from_string(cls, string):
        buf = create_string_buffer(string, len(string))
        sgio = SGIO.from_buffer(buf)
        sgio.source_buffer = buf
        return sgio

class LinuxCommandExecuter(CommandExecuterBase):
    def __init__(self, io, max_queue_size=DEFAULT_MAX_QUEUE_SIZE):
        super(LinuxCommandExecuter, self).__init__(max_queue_size)
        self.io = io

    def _os_prepare_to_send(self, command, packet_index):
        return SGIO.create(packet_index, command)

    def _os_send(self, os_data):
        yield self.io.write(os_data.to_raw())

    def _os_receive(self):
        raw = yield self.io.read(sizeof(SGIO))

        response_sgio = SGIO.from_string(raw)

        packet_id = response_sgio.pack_id
        request_sgio = self._get_os_data(packet_id)

        if response_sgio.status != 0:
            if (response_sgio.status & SCSI_STATUS_CHECK_CONDITION) != 0:
                yield (self._check_condition(string_at(response_sgio.sbp, SENSE_SIZE)), packet_id)
                raise StopIteration()
            
            yield (AsiSCSIError("SCSI response status is not zero: 0x%02x" % (response_sgio.status,)), packet_id)
            raise StopIteration()

        data = None
        if request_sgio.dxfer_direction == SG_DXFER_FROM_DEV and request_sgio.dxfer_len != 0:
            data = request_sgio.data_buffer.raw

        yield (data, packet_id)
