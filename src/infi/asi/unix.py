import os

from . import OSFile

class UnixFile(OSFile):
    def __init__(self, fd):
        self.fd = fd

    def read(self, size):
        return os.read(self.fd, size)

    def write(self, buffer):
        return os.write(self.fd, buffer)

    def close(self):
        os.close(self.fd)

# backward compatibility
OSFile = UnixFile