from infi.instruct import *

class CDB(Struct):
    _fields_ = []
    
    def create_datagram(self):
        return type(self).write_to_string(self)

    def execute(self, executer):
        raise NotImplementedError()
