from . import CommandExecuterBase, DEFAULT_TIMEOUT, SCSIReadCommand, SCSIWriteCommand
from . import gevent_friendly
from .errors import AsiSCSIError, AsiRequestQueueFullError
from ctypes import *
from logging import getLogger
from fcntl import ioctl
from struct import pack, unpack

logger = getLogger(__name__)

"""
from /usr/include/sys/scsi/impl/uscsi.h

struct uscsi_cmd {
        int             uscsi_flags;    /* read, write, etc. see below */
#ifdef _LITTLE_ENDIAN
        uchar_t         uscsi_status;   /* resulting scsi status */
        uchar_t         uscsi_reason;   /* resulting scsi_pkt */
#endif /* _LITTLE_ENDIAN */
#ifdef _BIG_ENDIAN
        uchar_t         uscsi_reason;   /* resulting scsi_pkt reason */
        uchar_t         uscsi_status;   /* resulting scsi status */
#endif /* _BIG_ENDIAN */
        short           uscsi_timeout;  /* Command Timeout */
        caddr_t         uscsi_cdb;      /* cdb to send to target */
        caddr_t         uscsi_bufaddr;  /* i/o source/destination */
        size_t          uscsi_buflen;   /* size of i/o to take place */
        size_t          uscsi_resid;    /* resid from i/o operation */
        uchar_t         uscsi_cdblen;   /* # of valid cdb bytes */
        uchar_t         uscsi_rqlen;    /* size of uscsi_rqbuf */
        uchar_t         uscsi_rqstatus; /* status of request sense cmd */
        uchar_t         uscsi_rqresid;  /* resid of request sense cmd */
        caddr_t         uscsi_rqbuf;    /* request sense buffer */
        ulong_t         uscsi_path_instance; /* private: hardware path */
};

/*** flags for uscsi_flags field ***/
/* generic flags */

#define USCSI_SILENT    0x00000001      /* no error messages */
#define USCSI_DIAGNOSE  0x00000002      /* fail if any error occurs */
/* NOTE: set USCSI_DIAGNOSE and you are responsible for all retry/recovery */
#define USCSI_ISOLATE   0x00000004      /* isolate from normal commands */
#define USCSI_READ      0x00000008      /* get data from device */
#define USCSI_WRITE     0x00000000      /* send data to device */

#define USCSI_RESET     0x00004000      /* Reset target */
#define USCSI_RESET_TARGET      \
                        USCSI_RESET     /* Reset target */
#define USCSI_RESET_ALL 0x00008000      /* Reset all targets */
#define USCSI_RQENABLE  0x00010000      /* Enable Request Sense extensions */
#define USCSI_RENEGOT   0x00020000      /* renegotiate wide/sync on next I/O */
#define USCSI_RESET_LUN 0x00040000      /* Reset logical unit */
#define USCSI_PATH_INSTANCE     \
                        0x00080000      /* use path instance for transport */

/* suitable for parallel SCSI bus only */
#define USCSI_ASYNC     0x00001000      /* Set bus to asynchronous mode */
#define USCSI_SYNC      0x00002000      /* Set bus to sync mode if possible */

/* User SCSI io control command */
#define USCSIIOC        (0x04 << 8)
#define USCSICMD        (USCSIIOC|201)  /* user scsi command */


/* uscsi_reason values: scsi_pkt(9S)(pkt_reason, pkt_state, ...) -> reason */
#define USCSI_REASON_NONE               0       /* normal completion */
#define USCSI_REASON_NONSPECIFIC        1       /* no defined pkt_reason map */
#define USCSI_REASON_TIMEOUT            2       /* timeout */
#define USCSI_REASON_DEVGONE            3       /* device gone */
#define USCSI_REASON_TRANSPORT          4       /* transport issue */
#define USCSI_REASON_PROTOCOL           5       /* protocol issue */
#define USCSI_REASON_RESERVED           0xFF    /* reserved */
"""
USCSI_SILENT = 0x00000001  # no error messages
USCSI_DIAGNOSE = 0x00000002  # fail if any error occurs
# NOTE: set USCSI_DIAGNOSE and you are responsible for all retry/recovery
USCSI_ISOLATE  = 0x00000004  # isolate from normal commands
USCSI_READ = 0x00000008  # get data from device
USCSI_WRITE = 0x00000000  # send data to device

USCSI_RESET = 0x00004000  # Reset target
USCSI_RESET_TARGET = USCSI_RESET  # Reset target
USCSI_RESET_ALL = 0x00008000  # Reset all targets
USCSI_RQENABLE = 0x00010000  # Enable Request Sense extensions
USCSI_RENEGOT = 0x00020000  # renegotiate wide/sync on next I/O
USCSI_RESET_LUN = 0x00040000  # Reset logical unit
USCSI_PATH_INSTANCE = 0x00080000  # use path instance for transport

USCSI_REASON = 0x00200000  # return uscsi_reason

# suitable for parallel SCSI bus only
USCSI_ASYNC = 0x00001000      # Set bus to asynchronous mode
USCSI_SYNC = 0x00002000      # Set bus to sync mode if possible

USCSIIOC = 0x04 << 8
USCSICMD = USCSIIOC | 201  # user scsi command

SENSE_SIZE = 0xFF

USCSI_DEFAULT_FLAGS = USCSI_REASON

class SCSICMD(Structure):
    _fields_ = [
    ("uscsi_flags", c_int),
    ("uscsi_status", c_short),  # Will be parsed as 2 byte variables - uscsi_status, uscsi_reason
    ("uscsi_timeout", c_short),
    ("uscsi_cdb", c_void_p),
    ("uscsi_bufaddr", c_void_p),
    ("uscsi_buflen", c_ulong),
    ("uscsi_resid", c_ulong),
    ("uscsi_cdblen", c_ubyte),
    ("uscsi_rqlen", c_ubyte),
    ("uscsi_rqstatus", c_ubyte),
    ("uscsi_rqresid", c_ubyte),
    ("uscsi_rqbuf", c_void_p),
    ("uscsi_path_instance", c_ulong)]

    def __init__(self, *args, **kwargs):
        super(SCSICMD, self).__init__(*args, **kwargs)
        self.source_buffer = None

    def init_sense_buffer(self):
        self.sense_buffer = create_string_buffer(SENSE_SIZE)
        self.uscsi_bufaddr = cast(self.sense_buffer, c_void_p)
        self.uscsi_buflen = sizeof(self.sense_buffer)

    def init_command_buffer(self, command):
        self.command_buffer = create_string_buffer(command, len(command))
        self.uscsi_cdb = cast(self.command_buffer, c_void_p)
        self.uscsi_cdblen = sizeof(self.command_buffer)

    def set_data_buffer(self, buf):
        if buf is not None:
            self.data_buffer = buf
            self.uscsi_bufaddr = cast(self.data_buffer, c_void_p)
            self.uscsi_buflen = sizeof(self.data_buffer)
        else:
            self.uscsi_bufaddr = 0
            self.uscsi_buflen = 0

    def to_raw(self):
        return self.source_buffer.raw

    def __repr__(self):
        return ("SCSICMD(uscsi_flags={self.uscsi_flags}, uscsi_status={self.uscsi_status}, " +
                "uscsi_timeout={self.uscsi_timeout}, uscsi_cdb={self.uscsi_cdb}, " +
                "uscsi_bufaddr={self.uscsi_bufaddr}, uscsi_buflen={self.uscsi_buflen}, uscsi_resid={self.uscsi_resid}, " +
                "uscsi_cdblen={self.uscsi_cdblen}, uscsi_rqlen={self.uscsi_rqlen}, uscsi_rqstatus={self.uscsi_rqstatus}, " +
                "uscsi_rqresid={self.uscsi_rqresid}, uscsi_rqbuf={self.uscsi_rqbuf}, " +
                "uscsi_path_instance={self.uscsi_path_instance})").format(self=self)

    @classmethod
    def create(cls, pack_id, command, timeout=0):
        buf = create_string_buffer(sizeof(SCSICMD))
        memset(buf, 0, sizeof(SCSICMD))
        scsicmd = SCSICMD.from_buffer(buf)
        scsicmd.source_buffer = buf
        scsicmd.init_sense_buffer()
        scsicmd.init_command_buffer(command.command)
        scsicmd.uscsi_timeout = timeout

        if isinstance(command, SCSIReadCommand):
            if command.max_response_length > 0:
                scsicmd.uscsi_flags = USCSI_READ | USCSI_DEFAULT_FLAGS
                scsicmd.set_data_buffer(create_string_buffer(command.max_response_length))
            else:
                scsicmd.uscsi_flags = USCSI_WRITE | USCSI_DEFAULT_FLAGS
                scsicmd.set_data_buffer(None)
        else:
            scsicmd.uscsi_flags = USCSI_WRITE | USCSI_DEFAULT_FLAGS
            scsicmd.set_data_buffer(create_string_buffer(command.data, len(command.data)))

        return scsicmd

    @classmethod
    def from_string(cls, string):
        buf = create_string_buffer(string, len(string))
        scsicmd = SCSICMD.from_buffer(buf)
        scsicmd.source_buffer = buf
        return scsicmd

    @classmethod
    def sizeof(cls):
        return sizeof(cls)

class SolarisCommandExecuter(CommandExecuterBase):
    def __init__(self, io, max_queue_size=1, timeout=DEFAULT_TIMEOUT):
        super(SolarisCommandExecuter, self).__init__(max_queue_size)
        self.io = io
        self.timeout = timeout

    def _os_prepare_to_send(self, command, packet_index):
        return SCSICMD.create(packet_index, command, self.timeout)

    def _os_send(self, os_data):
        self.buffer = os_data.to_raw()
        gevent_friendly(ioctl)(self.io.fd, USCSICMD, self.buffer)
        yield len(self.buffer)

    def _handle_raw_response(self, raw):
        response_cmd = SCSICMD.from_string(raw)

        packet_id = 0
        request_cmd = self._get_os_data(packet_id)
        response_status = pack("<h", response_cmd.uscsi_status)
        response_status_code = unpack("b", response_status[0])[0]
        response_reason_code = unpack("b", response_status[1])[0]

        if response_status_code != 0:
            return (AsiSCSIError(("SCSI response status is not zero: 0x%02x " +
                                 "(SCSI reason: 0x%02x)") %
                                (response_status_code, response_reason_code)), packet_id)
            raise StopIteration()

        if response_cmd.uscsi_rqstatus != 0:
            return (AsiSCSIError("SCSI request commmand status is not zero: 0x%02x" %
                                (response_cmd.uscsi_rqstatus)), packet_id)
            raise StopIteration()

        data = None
        if request_cmd.uscsi_flags & USCSI_READ and request_cmd.uscsi_buflen != 0:
            data = request_cmd.data_buffer.raw

        return (data, packet_id)

    def _os_receive(self):
        raw = yield self.buffer
        yield self._handle_raw_response(raw)
