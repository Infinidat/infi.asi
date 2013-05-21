from mock import patch
from unittest import TestCase
from infi import asi


@asi.gevent_friendly
def simple_function():
    return 1

def a_generator():
    inner_call = lambda n: n
    for i in range(2):
        yield asi.gevent_friendly(inner_call)(i)


class GeventFriendlyTestCase(TestCase):
    def test_simple_function(self):
        with patch.object(asi, "_gevent_friendly_sleep") as _gevent_friendly_sleep:
            self.assertEquals(simple_function(), 1)
        self.assertTrue(_gevent_friendly_sleep.called)

    def test_inside_generator(self):
        with patch.object(asi, "_gevent_friendly_sleep") as _gevent_friendly_sleep:
            self.assertEquals(list(a_generator()), [0, 1])
        self.assertEquals(_gevent_friendly_sleep.call_count, 2)
