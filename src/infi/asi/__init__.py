__import__("pkg_resources").declare_namespace(__name__)

import functools

class SCSICommand(object):
    def __init__(self, command):
        super(SCSICommand, self).__init__()
        self.command = command

class SCSIReadCommand(SCSICommand):
    def __init__(self, command, max_response_length):
        super(SCSIReadCommand, self).__init__(command)
        self.max_response_length = max_response_length

class SCSIWriteCommand(SCSICommand):
    def __init__(self, command, data):
        super(SCSIWriteCommand, self).__init__(command)
        self.data = data

class CommandExecuter(object):
    def call(self, command):
        raise NotImplementedError()
    
    def send(self, command, callback=None):
        raise NotImplementedError()

    def is_queue_full(self):
        raise NotImplementedError()

    def wait(self):
        raise NotImplementedError()

# TODO: maybe add a ReactorCommandExecuter that also adds a "register_response_listener()" that automatically reads
# the responses and calls a callback.

class Asi(object):
    def __init__(self, executer, call_wrapper):
        from .cdb.inquiry import standard_inquiry
        
        self.executer = executer
        self.call_wrapper = call_wrapper
        
        self.call = functools.partial(call_wrapper, self.executer.call)
        self.send = functools.partial(call_wrapper, self.executer.send)
        self.wait = functools.partial(call_wrapper, self.executer.wait)
        self.standard_inquiry = functools.partial(call_wrapper, functools.partial(standard_inquiry, self.executer))

class CommandExecuterAdapter(CommandExecuter):
    def __init__(self, executer, call_wrapper):
        super(CommandExecuterAdapter, self).__init__()
        self.executer = executer
        self.call_wrapper = call_wrapper

    def call(self, command):
        return self.call_wrapper(self.executer.call, command)
    
    def send(self, command, callback=None):
        return self.call_wrapper(self.executer.send, command, callback)

    def is_queue_full(self):
        return self.call_wrapper(self.executer.is_queue_full)

    def wait(self):
        return self.call_wrapper(self.executer.wait)

def create_platform_command_executer(*args, **kwargs):
    # TODO: per-OS
    from .linux import LinuxCommandExecuter
    return LinuxCommandExecuter(*args, **kwargs)

def create_sync_command_executer(*args, **kwargs):
    from .coroutines.sync_adapter import sync_call
    return CommandExecuterAdapter(create_platform_command_executer(*args, **kwargs), sync_call)

def create_microactor_command_executer(*args, **kwargs):
    from .coroutines.microactor_adapter import microactor_call
    return CommandExecuterAdapter(create_platform_command_executer(*args, **kwargs), microactor_call)

def create_sync_asi(io):
    from .coroutines.sync_adapter import sync_call
    executer = create_sync_command_executer(io)
    return Asi(executer, sync_call)

def create_microactor_asi(io):
    from .coroutines.microactor_adapter import microactor_call
    executer = create_microactor_command_executer(io)
    return Asi(executer, microactor_call)
