import os
import select

from . import OSFile

READ_TIMEOUT = 60    # seconds, more than enough


class UnixFile(OSFile):
    def __init__(self, fd):
        self.fd = fd

    def read(self, size):
        while not select.select([self.fd], [], [], READ_TIMEOUT)[0]:
            pass
        return os.read(self.fd, size)

    def write(self, buffer):
        return os.write(self.fd, buffer)

    def close(self):
        os.close(self.fd)

# backward compatibility
OSFile = UnixFile