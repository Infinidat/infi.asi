from infi.asi.executers import linux_sg as asi_context_linux
from infi.asi.coroutines.sync_adapter import sync_wait
from infi.asi.cdb.persist.output import PersistentReserveOutCommand, PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES
from infi.asi.cdb.persist.input import PersistentReserveInCommand, PERSISTENT_RESERVE_IN_SERVICE_ACTION_CODES

def read_keys_example(device):
    with asi_context_linux(device) as asi:
        command = PersistentReserveInCommand(service_action=PERSISTENT_RESERVE_IN_SERVICE_ACTION_CODES.READ_KEYS)
        response = sync_wait(command.execute(asi))
        return response

def register_key_example(device):
    with asi_context_linux(device) as asi:
        command = PersistentReserveOutCommand(
            service_action=PERSISTENT_RESERVE_OUT_SERVICE_ACTION_CODES.REGISTER,
            service_action_reservation_key=0xABBA)
        response = sync_wait(command.execute(asi))
        return response
