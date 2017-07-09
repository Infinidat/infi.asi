from binascii import hexlify

from infi.exceptools import InfiException

class AsiException(InfiException):
    pass

class AsiOSError(AsiException):
    pass

class AsiSCSIError(AsiException):
    pass

class AsiCheckConditionError(AsiSCSIError):
    def __init__(self, sense_buffer, sense_obj):
        super(AsiCheckConditionError, self).__init__("SCSI Check Condition status, sense %s [%s]" %
                                                     (repr(sense_obj), hexlify(sense_buffer)))
        self.sense_buffer = sense_buffer
        self.sense_obj = sense_obj

class AsiRequestQueueFullError(AsiException):
    def __init__(self):
        super(AsiRequestQueueFullError, self).__init__("Internal SCSI request queue is full, consider increasing it "
                                                       "using max_queue_size or call wait() to finish pending requests")

class AsiReservationConflictError(AsiSCSIError):
    def __init__(self):
        super(AsiReservationConflictError, self).__init__("SCSI reservation conflict")

class AsiInternalError(AsiException):
    pass
