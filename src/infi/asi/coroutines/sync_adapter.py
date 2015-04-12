import sys
import types

from .. import create_os_async_reactor, OSAsyncIOToken

class Coroutine(object):
    """ receives a coroutine generator and unwinds the stack """
    def __init__(self, generator):
        self.stack = [ generator ]
        self.args = None
        self.tb = None
        self.result = None
        self.done = False

    def _handle_async_io_token(self):
        raise NotImplementedError()

    def _next_step(self):
        """ invokes next generator in stack. returns False if execution should stop """
        try:
            if isinstance(self.args, BaseException):
                self.result = self.stack[-1].throw(self.args, None, self.tb)
            else:
                self.result = self.stack[-1].send(self.args)
            self.args = None
            if isinstance(self.result, types.GeneratorType):
                self.stack.append(self.result)
            elif isinstance(self.result, OSAsyncIOToken):
                return self._handle_async_io_token()
            else:
                self.args = self.result
        except StopIteration as e:
            self.stack.pop()
        except BaseException as e:
            self.tb = sys.exc_info()[2]
            self.stack.pop()
            if len(self.stack) == 0:
                raise
            self.args = e
        return True

    def loop(self):
        while len(self.stack) > 0:
            if not self._next_step():
                return self.result
        self.done = True
        return self.result

    def is_done(self):
        return self.done

    def get_result(self):
        return self.result

class AsyncCoroutine(Coroutine):
    def _handle_async_io_token(self):
        return False    # async IO - we should stop our loop and return control to the reactor

    def async_io_complete(self):
        """ Callback for reactor to signal that a blocking async IO has been completed """
        # current self.result is an Async IO Token, we can ask for its result now and continue with the stack
        self.args = self.result.get_result()

class SyncCoroutine(Coroutine):
    def _handle_async_io_token(self):
        # we just ask for a synhronous result from self.result which is the Async IO Token, and then continue
        self.args = self.result.get_result(block=True)
        return True

def sync_call(func, *init_args, **init_kwargs):
    stack = [ func(*init_args, **init_kwargs) ]
    return sync_wait(func(*init_args, **init_kwargs))

def sync_wait(generator):
    coroutine = SyncCoroutine(generator)
    result = coroutine.loop()
    if not coroutine.is_done():
        raise Exception("Synchronous coroutine was not completed")
    return result

def async_wait(*commands):
    reactor = create_os_async_reactor()
    return reactor.wait_for(*commands)
