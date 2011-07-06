from infi.exceptools import InfiException

class AsiException(InfiException):
    pass

class AsiOSError(AsiException):
    pass

class AsiSCSIError(AsiException):
    pass

class AsiRequestQueueFullError(AsiException):
    def __init__(self):
        super(AsiRequestQueueFullError, self).__init__("Internal SCSI request queue is full, consider increasing it "
                                                       "using max_queue_size or call wait() to finish pending requests")
class AsiInternalError(AsiException):
    pass
