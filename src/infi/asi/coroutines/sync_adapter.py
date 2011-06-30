import types

def sync_call(func, *init_args, **init_kwargs):
    stack = [ func(*init_args, **init_kwargs) ]
    return sync_wait(func(*init_args, **init_kwargs))

def sync_wait(generator):
    stack = [ generator ]
    args = None
    while len(stack) > 0:
        try:
            result = stack[-1].send(args)
            args = None
            if isinstance(result, types.GeneratorType):
                stack.append(result)
            else:
                args = result
        # TODO: catch other exceptions and pass them on the stack.
        except StopIteration, e:
            stack.pop()
    return result
