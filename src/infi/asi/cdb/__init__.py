from infi.instruct import *
from infi.instruct.buffer import Buffer


class CDB(Struct):
    _fields_ = []

    def create_datagram(self):
        return type(self).write_to_string(self)

    def execute(self, executer):
        raise NotImplementedError()


class CDBBuffer(Buffer):
    def create_datagram(self):
        return self.pack()

    def execute(self, executer):
        raise NotImplementedError()
