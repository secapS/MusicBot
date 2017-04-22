import asyncio
import traceback
import collections


class EventEmitter:
    """ TODO """
    def __init__(self):
        self._events = collections.defaultdict(list)
        self.loop = asyncio.get_event_loop()

    def emit(self, event, *args, **kwargs):
        """ TODO """
        if event not in self._events:
            return

        for cb in list(self._events[event]):
            # noinspection PyBroadException
            try:
                if asyncio.iscoroutinefunction(cb):
                    asyncio.ensure_future(cb(*args, **kwargs), loop=self.loop)
                else:
                    cb(*args, **kwargs)

            except:
                traceback.print_exc()

    def on(self, event, cb):
        """ TODO """
        self._events[event].append(cb)
        return self

    def off(self, event, cb):
        self._events[event].remove(cb)

        if not self._events[event]:
            del self._events[event]

        return self

    def once(self, event, cb):
        """ TODO """
        def callback(*args, **kwargs):
            """ TODO """
            self.off(event, callback)
            return cb(*args, **kwargs)

        return self.on(event, callback)
