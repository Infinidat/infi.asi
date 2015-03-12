from infi.asi.coroutines.sync_adapter import sync_wait

def test_simple_coroutines():
    def bar():
        yield 5
    
    def foo():
        i = yield bar()
        yield i

    res = sync_wait(foo())
    assert res == 5
    

def __test_exception():
    def kar():
        yield 5
        
    def bar():
        i = yield kar()
        raise Exception("my bad")
    
    def foo():
        try:
            i = yield bar()
        except Exception:
            i = 7
        yield i

    res = sync_wait(foo())
    assert res == 7

def test_using_generator():
    def kar():
        return 5
        
    def bar():
        for i in range(5):
            yield i

    def foo():
        i = yield kar()
        for n in bar():
            i += 1
        yield i

    res = sync_wait(foo())
    assert res == 10
