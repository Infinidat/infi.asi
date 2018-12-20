from . import CommandExecuterBase, DEFAULT_MAX_QUEUE_SIZE, DEFAULT_TIMEOUT, SCSIReadCommand, SCSIWriteCommand
from . import SCSI_STATUS_CODES, gevent_friendly
from .errors import AsiSCSIError, AsiRequestQueueFullError, AsiReservationConflictError
from ctypes import *
from logging import getLogger

logger = getLogger(__name__)

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
#define SG_INFO_OK_MASK    0x1
#define SG_INFO_OK    0x0    /* no sense, host nor driver "noise" */
#define SG_INFO_CHECK    0x1     /* something abnormal happened */

#define SG_INFO_DIRECT_IO_MASK    0x6
#define SG_INFO_INDIRECT_IO     0x0    /* data xfer via kernel buffers (or no xfer) */
#define SG_INFO_DIRECT_IO     0x2    /* direct IO requested and performed */
#define SG_INFO_MIXED_IO     0x4    /* part direct, part indirect IO */
"""
SG_DXFER_NONE = -1
SG_DXFER_TO_DEV = -2
SG_DXFER_FROM_DEV = -3
SG_DXFER_TO_FROM_DEV = -4
SG_FLAG_DIRECT_IO = 1
SG_FLAG_LUN_INHIBIT = 2
SG_FLAG_NO_DXFER = 0x10000

# Driver errors (from sg_err.h). The lower nibble is ORed with the upper one.

DRIVER_STATUS_CODES = dict(
    SG_ERR_DRIVER_OK = 0x00,  # Typically no suggestion
    SG_ERR_DRIVER_BUSY = 0x01,
    SG_ERR_DRIVER_SOFT = 0x02,
    SG_ERR_DRIVER_MEDIA = 0x03,
    SG_ERR_DRIVER_ERROR = 0x04,
    SG_ERR_DRIVER_INVALID = 0x05,
    SG_ERR_DRIVER_TIMEOUT = 0x06,  # Adapter driver is unable to control the SCSI bus to its is setting its devices offline (and giving up)
    SG_ERR_DRIVER_HARD = 0x07,
    SG_ERR_DRIVER_SENSE = 0x08,  # Implies sense_buffer output above status 'or'ed with one of the following suggestions
    SG_ERR_SUGGEST_RETRY = 0x10,
    SG_ERR_SUGGEST_ABORT = 0x20,
    SG_ERR_SUGGEST_REMAP = 0x30,
    SG_ERR_SUGGEST_DIE = 0x40,
    SG_ERR_SUGGEST_SENSE = 0x80
)

# Host errors (from sg_err.h)
HOST_STATUS_CODES = dict(
    SG_ERR_DID_OK = 0x00,  # NO error
    SG_ERR_DID_NO_CONNECT = 0x01,  # Couldn't connect before timeout period
    SG_ERR_DID_BUS_BUSY = 0x02,  # BUS stayed busy through time out period
    SG_ERR_DID_TIME_OUT = 0x03,  # TIMED OUT for other reason (often this an unexpected device selection timeout)
    SG_ERR_DID_BAD_TARGET = 0x04,  # BAD target, device not responding?
    SG_ERR_DID_ABORT = 0x05,  # Told to abort for some other reason. From lk 2.4.15 the SCSI subsystem supports 16 byte commands however few adapter drivers do. Those HBA drivers that don't support 16 byte commands will yield this error code if a 16 byte command is passed to a SCSI device they control.
    SG_ERR_DID_PARITY = 0x06,  # Parity error. Older SCSI parallel buses have a parity bit for error detection. This probably indicates a cable or termination problem.
    SG_ERR_DID_ERROR = 0x07,  # Internal error detected in the host adapter. This may not be fatal (and the command may have succeeded). The aic7xxx and sym53c8xx adapter drivers sometimes report this for data underruns or overruns. [9]
    SG_ERR_DID_RESET = 0x08,  # The SCSI bus (or this device) has been reset. Any SCSI device on a SCSI bus is capable of instigating a reset.
    SG_ERR_DID_BAD_INTR = 0x09,  # Got an interrupt we weren't expecting
    SG_ERR_DID_PASSTHROUGH = 0x0a,  # Force command past mid-layer
    SG_ERR_DID_SOFT_ERROR = 0x0b  # The low level driver wants a retry
)

SENSE_SIZE = 0xFF


def prettify_status(code, status_dict):
    code_string = [key for key, value in status_dict.items() if value == code] or ['']
    return "%s 0x%02x" % (code_string[0], code)


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
            self.dxferp = 0
            self.dxfer_len = 0

    def to_raw(self):
        return self.source_buffer.raw

    def __repr__(self):
        return ("SGIO(interface_id={self.interface_id}, dxfer_direction={self.dxfer_direction}, " +
                "cmd_len={self.cmd_len}, mx_sb_len={self.mx_sb_len}, iovec_count={self.iovec_count}, " +
                "dxfer_len={self.dxfer_len}, dxferp={self.dxferp}, cmdp={self.cmdp}, sbp={self.sbp}, " +
                "timeout={self.timeout}, flags={self.flags}, pack_id={self.pack_id}, usr_ptr={self.usr_ptr}, " +
                "status={self.status}, masked_status={self.masked_status}, msg_status={self.msg_status}, " +
                "sb_len_wr={self.sb_len_wr}, host_status={self.host_status}, driver_status={self.driver_status}, " +
                "resid={self.resid}, duration={self.duration}, info={self.info})").format(self=self)

    @classmethod
    def create(cls, pack_id, command, timeout=0):
        buf = create_string_buffer(sizeof(SGIO))
        memset(buf, 0, sizeof(SGIO))
        sgio = SGIO.from_buffer(buf)
        sgio.source_buffer = buf
        sgio.interface_id = ord('S')
        sgio.pack_id = pack_id
        sgio.init_sense_buffer()
        sgio.init_command_buffer(command.command)
        sgio.timeout = timeout

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

    @classmethod
    def sizeof(cls):
        return sizeof(cls)

class LinuxCommandExecuter(CommandExecuterBase):
    def __init__(self, io, max_queue_size=DEFAULT_MAX_QUEUE_SIZE, timeout=DEFAULT_TIMEOUT):
        super(LinuxCommandExecuter, self).__init__(max_queue_size)
        self.io = io
        self.timeout = timeout

    def _os_prepare_to_send(self, command, packet_index):
        return SGIO.create(packet_index, command, self.timeout)

    def _os_send(self, os_data):
        yield gevent_friendly(self.io.write)(os_data.to_raw())

    def _handle_raw_response(self, raw):
        response_sgio = SGIO.from_string(raw)

        packet_id = response_sgio.pack_id
        request_sgio = self._get_os_data(packet_id)

        if (response_sgio.status & SCSI_STATUS_CODES['SCSI_STATUS_CHECK_CONDITION']) != 0 or \
                (response_sgio.driver_status & DRIVER_STATUS_CODES['SG_ERR_DRIVER_SENSE'] != 0):
            logger.debug("response_sgio.status = 0x{:x}".format(response_sgio.status))
            logger.debug("response_sgio.driver_status = 0x{:x}".format(response_sgio.driver_status))
            return (self._check_condition(string_at(response_sgio.sbp, SENSE_SIZE)), packet_id)
            raise StopIteration()

        if response_sgio.status != 0:
            if response_sgio.host_status == 0x07:
                return (AsiRequestQueueFullError(), packet_id)
            if response_sgio.host_status == SCSI_STATUS_CODES['SCSI_STATUS_RESERVATION_CONFLICT']:
                return (AsiReservationConflictError(), packet_id)
            error = AsiSCSIError(("SCSI response status is not zero: %s" +
                                  "(driver status: %s, host status: %s)") %
                                 (prettify_status(response_sgio.status, SCSI_STATUS_CODES),
                                  prettify_status(response_sgio.driver_status & 0x0f, DRIVER_STATUS_CODES),
                                  prettify_status(response_sgio.host_status, HOST_STATUS_CODES)))
            return (error, packet_id)
            raise StopIteration()

        if (response_sgio.driver_status & 0x0F) != 0:
            error = AsiSCSIError("SCSI driver response status is not zero: %s (host status: %s)" %
                                (prettify_status(response_sgio.status, SCSI_STATUS_CODES),
                                 prettify_status(response_sgio.driver_status & 0x0f, DRIVER_STATUS_CODES)))
            return (error, packet_id)
            raise StopIteration()

        if response_sgio.host_status != 0:
            error = AsiSCSIError(("SCSI host status is not zero: %s" +
                                  "(driver status: %s, host status: %s)") %
                                 (prettify_status(response_sgio.status, SCSI_STATUS_CODES),
                                  prettify_status(response_sgio.driver_status & 0x0f, DRIVER_STATUS_CODES),
                                  prettify_status(response_sgio.host_status, HOST_STATUS_CODES)))
            return (error, packet_id)
            raise StopIteration()

        data = None
        if request_sgio.dxfer_direction == SG_DXFER_FROM_DEV and request_sgio.dxfer_len != 0:
            data = request_sgio.data_buffer.raw

        return (data, packet_id)

    def _os_receive(self):
        raw = yield gevent_friendly(self.io.read)(SGIO.sizeof())
        yield self._handle_raw_response(raw)

SG_IO = 0x2285


class LinuxIoctlCommandExecuter(LinuxCommandExecuter):
    def __init__(self, io, max_queue_size=1, timeout=DEFAULT_TIMEOUT):
        super(LinuxIoctlCommandExecuter, self).__init__(io, max_queue_size, timeout)
        self.io = io
        self.timeout = timeout

    def _os_send(self, os_data):
        from fcntl import ioctl
        self.buffer = os_data.to_raw()
        gevent_friendly(ioctl)(self.io.fd, SG_IO, self.buffer)
        yield len(self.buffer)

    def _os_receive(self):
        raw = yield self.buffer
        yield self._handle_raw_response(raw)
