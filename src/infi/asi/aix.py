from . import CommandExecuterBase, DEFAULT_TIMEOUT_IN_SEC, SCSIReadCommand, SCSIWriteCommand
from . import SCSI_STATUS_CODES, gevent_friendly
from .linux import prettify_status, SENSE_SIZE
from .errors import AsiSCSIError, AsiOSError
from ctypes import *
from logging import getLogger
import six

logger = getLogger(__name__)


# links to IBM documentation:
# DK_PASSTHRU info here: http://www-01.ibm.com/support/knowledgecenter/ssw_aix_61/com.ibm.aix.ktechrf2/scsidisk.htm
# SCIOCMD (not used): http://www-01.ibm.com/support/knowledgecenter/ssw_aix_71/com.ibm.aix.ktechrf2/SCIOCMD.htm

"""
from /usr/include/sys/scsi_buf.h

struct sc_passthru {

      ushort version;                /* The version number of this       */
                                     /* structure. This allows the       */
                                     /* structure to expand in the       */
                                     /* future.                          */
/*  For this structure the version field MUST have a value of            */
/*  SCSI_VERSION_2                                                       */

      uchar status_validity;         /* 0 = no valid status              */
                                     /* Valid values for this are defined*/
                                     /* under the status_validity field  */
                                     /* of the sc_buf structure.         */
                                     /* 1 = valid SCSI bus status only   */
                                     /* 2 = valid adapter status only    */
      uchar scsi_bus_status;         /* SCSI bus status (if valid)       */
                                     /* Valid values for this are defined*/
                                     /* under the scsi_bus_status field  */
                                     /* of the sc_buf structure          */
      uchar adap_status_type;        /* These flags are set by the SCSI  */
                                     /* adapter driver when a command is */
                                     /* returned. It indicates the       */
                                     /* type of adapter error            */
#define SC_ADAP_SC_ERR 0x1           /* The adapter status is from an    */
                                     /* parallel SCSI adapter            */
#define SC_ADAP_SAM_ERR 0x2          /* The adapter status is from an    */
                                     /* SAM (SCSI-3 Architecture Model)  */
                                     /* compliant adapter                */
      uchar adapter_status;          /* Adapter status (if valid)        */
                                     /* if adap_status_type is           */
                                     /* SC_ADAP_SC_ERR then see scsi.h   */
                                     /* for sc_buf general_card_status   */
                                     /* definition                       */
                                     /* if adap_status_type is           */
                                     /* SC_ADAP_SAM_ERR then see         */
                                     /* scsi_buf.h for scsi_buf          */
                                     /* adapter_status definitions       */

      uchar adap_set_flags;          /* These flags are set by the SCSI  */
                                     /* adapter driver when a command is */
                                     /* returned.                        */
#define SC_AUTOSENSE_DATA_VALID 0x1  /* This indicates the device        */
                                     /* driver has placed the autosense  */
                                     /* data for this command failure    */
                                     /* in the buffer referenced by the  */
                                     /* field autosense_buffer_ptr.      */
#define SC_RET_ID               0x2  /* The scsi_id of this device is    */
                     /* different than the scsi_id       */
                     /* provided by the caller. The      */
                     /* scsi_id field has been updated   */
                     /* with current scsi_id for the     */
                     /* device with this world wide name.*/

      uchar add_device_status;       /* Additional device status.        */
                                     /* For FCP devices, this field      */
                                     /* contains the FCP response code.  */

      uchar adap_q_status;           /* used to return back whether or   */
                                     /* or not the SCSI adapter driver   */
                                     /* and SCSI adapter cleared their   */
                                     /* queue for this device or not.    */
                                     /* A value of zero implies that     */
                                     /* the device's queue at the        */
                                     /* adapter is cleared.              */
                                     /* A value of SC_DID_NOT_CLEAR_Q,   */
                                     /* defined in scsi.h, implies that  */
                                     /* the device's queue at the        */
                                     /* adapter has not be cleared.      */
      uchar q_tag_msg;               /* Used to pass down Queue Tag      */
                                     /* message fields of SC_NO_Q,       */
                                     /* SC_SIMPLE_Q, SC_HEAD_OF_Q,       */
                                     /* SC_ORDERED_Q, or SC_ACA_Q,       */
                                     /* defined above in sc_buf's        */
                                     /* definition.                      */
      uchar flags;                   /* Valid values are B_READ, B_WRITE */
                                     /* (defined in buf.h) and SC_NODISC */
                                     /* SC_ASYNC (defined in the scsi    */
                                     /* struct above)                    */
      uchar devflags;                /* device flags set by caller       */
#define SC_QUIESCE_IO 0x0            /* Quiesce device before issuing    */
                                     /* this passthru command.           */
#define SC_MIX_IO     0x1            /* Do not quiesce device before     */
                                     /* issuing this command. Instead    */
                                     /* allow command to be mixed with   */
                                     /* other I/O requests               */
      uchar q_flags;                 /* Used to tell the SCSI adapter    */
                                     /* driver, and SCSI adapter whether */
                                     /* or not it should clear or resume */
                                     /* its queue. This is done via the  */
                                     /* defines SC_Q_CLR,SC_Q_RESUME,    */
                                     /* or SC_CLEAR_ACA defined above    */
                                     /* in sc_buf.                       */
      ushort command_length;         /* Length of SCSI command block     */

      ushort einval_arg;             /* If this request is failed with   */
                                     /* an errno of EINVAL due to an     */
                                     /* invalid setting in some field,   */
                                     /* then this field will provide the */
                                     /* number of that invalid field.    */
#define SC_PASSTHRU_INV_VERS       1 /* Version field is invalid         */
#define SC_PASSTHRU_INV_Q_TAG_MSG  9 /* q_tag_msg field is invalid       */
#define SC_PASSTHRU_INV_FLAGS     10 /* flags field is invalid           */
#define SC_PASSTHRU_INV_DEVFLAGS  11 /* devflags field is invalid        */
#define SC_PASSTHRU_INV_Q_FLAGS   12 /* q_flags field is invalid         */
#define SC_PASSTHRU_INV_CDB_LEN   13 /* command_length field is invalid  */
#define SC_PASSTHRU_INV_AS_LEN    15 /* autosense_length field is invalid*/
#define SC_PASSTHRU_INV_CDB       16 /* scsi_cdb field is invalid        */
#define SC_PASSTHRU_INV_TO        17 /* timeout_value field is invalid   */
#define SC_PASSTHRU_INV_D_LEN     18 /* data_length field is invalid     */
#define SC_PASSTHRU_INV_SID       19 /* scsi_id field is invalid         */
#define SC_PASSTHRU_INV_LUN       20 /* lun_id field is invalid          */
#define SC_PASSTHRU_INV_BUFF      21 /* buffer field is invalid          */
#define SC_PASSTHRU_INV_AS_BUFF   22 /* autosense_buffer_ptr is invalid  */
#define SC_PASSTHRU_INV_VAR_CDB_LEN 23 /* varialbe_cdb_length field is   */
                                     /* invalid                          */
#define SC_PASSTHRU_INV_VAR_CDB   24 /* variable_cdb_ptr field is invalid*/

      ushort autosense_length;       /* This specifies the maximum size  */
                                     /* in bytes of the auto sense       */
                                     /* buffer referenced by the         */
                                     /* autosense_buffer_ptr field.      */

      uint timeout_value;            /* Time-out value in seconds        */


      unsigned long long data_length;/* Bytes of data to be transferred  */
      unsigned long long scsi_id;    /* This is the 64-bit SCSI ID for   */
                                     /* the device.                      */

      unsigned long long lun_id;     /* This is the 64-bit lun ID for    */
                                     /* the device.                      */
      char *buffer;                  /* Pointer to transfer data buffer  */
      char *autosense_buffer_ptr;    /* A pointer to the caller's        */
                                     /* autosense buffer for this SCSI   */
                                     /* command.                         */
                                     /* NOTE: if this is NULL            */
                                     /* then the adapter driver will     */
                                     /* throw away the sense data.       */
      uchar scsi_cdb[SC_PASSTHRU_CDB_LEN];/* SCSI command descriptor     */
                     /* block                            */
                                     /* The target's world wide name     */
      unsigned long long world_wide_name;

                     /* The target's node name           */
      unsigned long long node_name;

      uint variable_cdb_length;      /* length of variable cdb referring */
                                     /* to the variable_cdb_ptr.         */

      char *variable_cdb_ptr;        /* pointer to a buffer which holds  */
                                     /* the variable SCSI cdb.           */

      unsigned long long residual;   /* bytes not xferred after error.   */

};
"""

DK_PASSTHRU = 23
B_WRITE = 0
B_READ = 1
SC_PASSTHRU_CDB_LEN = 64

# status_validity values
STATUS_VALIDITY_CODES = dict(
    SC_SCSI_ERROR = 1,
    SC_ADAPTER_ERROR = 2
)

SCSI_VERSION_0 = 0x00
SCSI_VERSION_1 = 0x01
SCSI_VERSION_2 = 0x02
SCSI_VERSION_3 = 0x03
SCSI_VERSION_4 = 0x04

SC_QUIESCE_IO =  0x0          # Quiesce device before issuing
SC_MIX_IO =      0x1          # Do not quiesce device before

SCSI_STATUS_MASK = 0x1e  # mask for useful bits

ADAPTER_STATUS_CODES = dict(
     SCSI_HOST_IO_BUS_ERR =      0x01,  # indicates a Host I/O Bus error
     SCSI_TRANSPORT_FAULT =      0x02,  # indicates a failure of the
     SCSI_CMD_TIMEOUT =          0x03,  # the command did not complete
     SCSI_NO_DEVICE_RESPONSE =   0x04,  # the target device did not
     SCSI_ADAPTER_HDW_FAILURE =  0x05,  # the adapter is indicating a
     SCSI_ADAPTER_SFW_FAILURE =  0x06,  # the adapter is indicating a
     SCSI_WW_NAME_CHANGE =       0x07,  # the adapter detected that the
     SCSI_FUSE_OR_TERMINAL_PWR = 0x08,  # the adapter is indicating a
     SCSI_TRANSPORT_RESET =      0x09,  # the adapter detected an external
     SCSI_TRANSPORT_BUSY =       0x0a,  # the transport layer is busy
     SCSI_TRANSPORT_DEAD =       0x0b,  # the transport layer is
     SCSI_VERIFY_DEVICE =        0x0c,  # the adapter is indicating that
     SCSI_TRANSPORT_MIGRATED =   0x0d,  # transport migrated
     SCSI_ERROR_NO_RETRY =       0x0e,  # An error occured, do not retry
     SCSI_ERROR_DELAY_LOG =      0x0f,  # An error occured, only log an
)


EINVAL_CODES = dict(
    SC_PASSTHRU_INV_VERS =         1,  # Version field is invalid
    SC_PASSTHRU_INV_Q_TAG_MSG =    9,  # q_tag_msg field is invalid
    SC_PASSTHRU_INV_FLAGS =       10,  # flags field is invalid
    SC_PASSTHRU_INV_DEVFLAGS =    11,  # devflags field is invalid
    SC_PASSTHRU_INV_Q_FLAGS =     12,  # q_flags field is invalid
    SC_PASSTHRU_INV_CDB_LEN =     13,  # command_length field is invalid
    SC_PASSTHRU_INV_AS_LEN =      15,  # autosense_length field is invalid
    SC_PASSTHRU_INV_CDB =         16,  # scsi_cdb field is invalid
    SC_PASSTHRU_INV_TO =          17,  # timeout_value field is invalid
    SC_PASSTHRU_INV_D_LEN =       18,  # data_length field is invalid
    SC_PASSTHRU_INV_SID =         19,  # scsi_id field is invalid
    SC_PASSTHRU_INV_LUN =         20,  # lun_id field is invalid
    SC_PASSTHRU_INV_BUFF =        21,  # buffer field is invalid
    SC_PASSTHRU_INV_AS_BUFF =     22,  # autosense_buffer_ptr is invalid
    SC_PASSTHRU_INV_VAR_CDB_LEN = 23,  # varialbe_cdb_length field is
    SC_PASSTHRU_INV_VAR_CDB =     24,  # variable_cdb_ptr field is invalid
)


class AixAsiSCSIError(AsiSCSIError):
    def __init__(self, msg, os_data):
        validity = prettify_status(os_data.status_validity, STATUS_VALIDITY_CODES)
        scsi_bus_status = prettify_status(os_data.scsi_bus_status & SCSI_STATUS_MASK, SCSI_STATUS_CODES)
        adapter_status = prettify_status(os_data.adapter_status, ADAPTER_STATUS_CODES)
        status_string = "{}, validity={}, scsi_bus_status={}, adapter_status={}"
        super(AixAsiSCSIError, self).__init__(status_string.format(msg, validity, scsi_bus_status, adapter_status))


class sc_passthru(Structure):
    _fields_ = [
        ("version", c_ushort),
        ("status_validity", c_ubyte),
        ("scsi_bus_status", c_ubyte),
        ("adap_status_type", c_ubyte),
        ("adapter_status", c_ubyte),
        ("adap_set_flags", c_ubyte),
        ("add_device_status", c_ubyte),
        ("adap_q_status", c_ubyte),
        ("q_tag_msg", c_ubyte),
        ("flags", c_ubyte),
        ("devflags", c_ubyte),
        ("q_flags", c_ubyte),
        ("command_length", c_ushort),
        ("einval_arg", c_ushort),
        ("autosense_length", c_ushort),
        ("timeout_value", c_uint),
        ("data_length", c_ulonglong),
        ("scsi_id", c_ulonglong),
        ("lun_id", c_ulonglong),
        ("buffer", c_void_p),
        ("autosense_buffer_ptr", c_void_p),
        ("scsi_cdb", ARRAY(c_ubyte, SC_PASSTHRU_CDB_LEN)),
        ("world_wide_name", c_ulonglong),
        ("node_name", c_ulonglong),
        ("variable_cdb_length", c_uint),
        ("variable_cdb_ptr", c_void_p),
        ("residual", c_ulonglong),
    ]

    def __init__(self, *args, **kwargs):
        super(sc_passthru, self).__init__(*args, **kwargs)
        self.source_buffer = None

    def init_sense_buffer(self):
        self.sense_buffer = create_string_buffer(SENSE_SIZE)
        self.autosense_buffer_ptr = cast(self.sense_buffer, c_void_p)
        self.autosense_length = sizeof(self.sense_buffer)

    def init_command_buffer(self, command):
        self.command_buffer = create_string_buffer(command, len(command))
        for i in range(SC_PASSTHRU_CDB_LEN):
            self.scsi_cdb[i] = 0
        for i in range(min(SC_PASSTHRU_CDB_LEN, len(command))):
            self.scsi_cdb[i] = six.indexbytes(command, i)  # ord(command[i])
        self.command_length = len(command)

    def set_data_buffer(self, buf):
        if buf is not None:
            self.data_buffer = buf
            self.buffer = cast(self.data_buffer, c_void_p)
            self.data_length = sizeof(self.data_buffer)
        else:
            self.data_length = 0

    def to_raw(self):
        return self.source_buffer.raw

    def __repr__(self):
        values = '\n\t'.join(["{}={!r}".format(field[0], getattr(self, field[0])) for field in self._fields_])
        return "{}({})".format(self.__class__.__name__, values)

    @classmethod
    def create(cls, pack_id, io, command, timeout=0):
        buf = create_string_buffer(sizeof(sc_passthru))
        memset(buf, 0, sizeof(sc_passthru))
        scsicmd = sc_passthru.from_buffer(buf)
        scsicmd.source_buffer = buf
        scsicmd.version = SCSI_VERSION_2
        scsicmd.init_sense_buffer()
        scsicmd.init_command_buffer(command.command)
        scsicmd.timeout_value = timeout
        scsicmd.devflags = SC_MIX_IO

        if isinstance(command, SCSIReadCommand):
            if command.max_response_length > 0:
                scsicmd.flags = B_READ
                scsicmd.set_data_buffer(create_string_buffer(command.max_response_length))
            else:
                scsicmd.flags = B_WRITE
                scsicmd.set_data_buffer(None)
        else:
            scsicmd.flags = B_WRITE
            scsicmd.set_data_buffer(create_string_buffer(command.data, len(command.data)))
        return scsicmd

    @classmethod
    def from_string(cls, string):
        buf = create_string_buffer(string, len(string))
        scsicmd = sc_passthru.from_buffer(buf)
        scsicmd.source_buffer = buf
        return scsicmd

    @classmethod
    def sizeof(cls):
        return sizeof(cls)

class AixCommandExecuter(CommandExecuterBase):
    def __init__(self, io, max_queue_size=1, timeout=DEFAULT_TIMEOUT_IN_SEC):
        super(AixCommandExecuter, self).__init__(max_queue_size)
        self.io = io
        self.timeout = timeout

    def _os_prepare_to_send(self, command, packet_index):
        return sc_passthru.create(packet_index, self.io, command, self.timeout)

    def _os_send(self, os_data):
        from fcntl import ioctl
        try:
            gevent_friendly(ioctl)(self.io.fd, DK_PASSTHRU, addressof(os_data))
        except IOError:
            if os_data.einval_arg != 0:
                msg = "ioctl failed, invalid argument: {}"
                raise AsiOSError(msg.format(prettify_status(os_data.einval_arg, EINVAL_CODES)))
            elif os_data.status_validity == 0:
                # no valid status to parse in _handle_raw_response
                raise AsiOSError("ioctl failed, no valid status")
        self.buffer = os_data.to_raw()
        yield len(self.buffer)

    def _handle_raw_response(self, raw):
        response_cmd = sc_passthru.from_string(raw)

        packet_id = 0
        request_cmd = self._get_os_data(packet_id)

        if response_cmd.status_validity != 0:
            if response_cmd.status_validity == STATUS_VALIDITY_CODES['SC_SCSI_ERROR']:
                scsi_status = response_cmd.scsi_bus_status & SCSI_STATUS_MASK
                if (scsi_status & SCSI_STATUS_CODES['SCSI_STATUS_CHECK_CONDITION']) != 0:
                    return (self._check_condition(string_at(response_cmd.autosense_buffer_ptr, SENSE_SIZE)), packet_id)
                    raise StopIteration()
                return (AixAsiSCSIError("SCSI bus response status is not zero", response_cmd), packet_id)
                raise StopIteration()
            elif response_cmd.status_validity == STATUS_VALIDITY_CODES['SC_ADAPTER_ERROR']:
                return (AixAsiSCSIError("SCSI adapter response status is not zero", response_cmd), packet_id)
                raise StopIteration()
            else:
                return (AixAsiSCSIError("SCSI response status validity unknown", response_cmd), packet_id)
                raise StopIteration()

        data = None
        if request_cmd.flags & B_READ and request_cmd.data_length != 0:
            data = request_cmd.data_buffer.raw

        return (data, packet_id)

    def _os_receive(self):
        raw = yield self.buffer
        yield self._handle_raw_response(raw)
