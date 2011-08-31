import binascii

class DebugStream(object):
    def __init__(self, buffer):
        self.buffer = buffer
        
    def read(self, size):
        result = self.buffer[0:size]
        print("read(%d): %s" % (size, binascii.hexlify(result)))
        self.buffer = self.buffer[size:]
        return result
