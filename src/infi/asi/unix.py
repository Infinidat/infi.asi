import os
import select
import time

from . import OSFile


class UnixFile(OSFile):
    READ_TIMEOUT = 60    # seconds, more than enough

    def __init__(self, fd, read_timeout=READ_TIMEOUT):
        self.fd = fd
        self._read_timeout = read_timeout

    def read(self, size):
        start_time = time.time()

        # A time-out value of zero specifies a poll and never blocks:
        while not select.select([self.fd], [], [], 0)[0]:
            time.sleep(0.01)
            if time.time() > start_time + self._read_timeout:
                raise IOError("Timeout while waiting for file descriptor to become readable")

        return os.read(self.fd, size)

    def write(self, buffer):
        return os.write(self.fd, buffer)

    def close(self):
        os.close(self.fd)

# backward compatibility
OSFile = UnixFile