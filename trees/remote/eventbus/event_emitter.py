import asyncio
import functools

ALL_HANDLER = "*"
NO_HANDLER = "!"


async def _g():
    pass


type_coro = type(_g())


class EventEmitter:
    """
    A class that represents an event emitter.

    The EventEmitter class allows registering event handlers for specific topics and emitting events to those handlers.
    """

    def __init__(self, sync_queue_size=20, pause=0.1):
        """
        Initializes the event emitter object.

        Args:
            sync_queue_size (int): The maximum size of the emit_sync queue.
            pause (float): Delay between submission of sync events.
        """
        self.event_map = {}
        self.event_queue = None
        self.sync_queue_size = sync_queue_size
        self.pause = pause

    def on(self, *topics):
        """
        Decorator function to register a handler for one or more topics.

        Args:
            *topics: Variable number of topics to listen to.

            The following topics have special meaning:
            - '*': A handler that listens to all topics.
            - '!': A handler that listens to topics that have no registered handlers.

        Returns:
            A decorator function that wraps the provided function and adds it to the event map.

        Example:
            @event_emitter.on('topic1', 'topic2')
            def my_listener(topic, **kwargs):
                print(f'Received topic: {topic} with args: {kwargs}')
        """

        def decorator_on(func):
            for topic in topics:
                if topic not in self.event_map:
                    self.event_map[topic] = []
                self.event_map[topic].append(func)

            @functools.wraps(func)
            def wrapper_on(event):
                return func(event)

            for k, v in self.event_map.items():
                if k in topics:
                    v[-1] = (v[-1], id(wrapper_on))

            return wrapper_on

        return decorator_on

    def off(self, func):
        """
        Unregisters a function from the event emitter.

        Args:
            func: The previously registered (with @on ...) handler to be unregistered.
        """
        for k, v in self.event_map.items():
            for i, f in enumerate(v):
                if f[-1] == id(func):
                    v.pop(i)
                    break

    def clear(self):
        """
        Clears all registered event handlers.
        """
        self.event_map = {}

    async def emit(self, event):
        """
        Emits an event to all registered event handlers for the given topic.

        Args:
            event (dict)
        """
        topic = event.get("topic", event.get("type"))
        if topic in self.event_map:
            for func in self.event_map[topic]:
                await self._call_handler(func, event)
        else:
            for func in self.event_map.get(NO_HANDLER, ()):
                await self._call_handler(func, event)
        for func in self.event_map.get(ALL_HANDLER, ()):
            await self._call_handler(func, event)

    def emit_sync(self, event):
        """
        Emit event from synchronous code.

        Args:
            topic (str): The topic of the event.
            **args: Additional keyword arguments to pass along with the event.
        """
        if self.event_queue is None:
            try:
                self.event_queue = asyncio.Queue(maxsize=self.sync_queue_size)
            except AttributeError:
                from asyncio_extra import queue

                self.event_queue = queue.Queue(maxsize=self.sync_queue_size)
            asyncio.create_task(self._sync_emit_task(self.pause))

        try:
            self.event_queue.put_nowait(event)
        except asyncio.QueueFull:
            pass
            # Note: no log message - as that would generate another emit_sync event!
            print("***** sync event queue overflow")

    async def _sync_emit_task(self, sleep):
        """
        Task that asynchronously emits events submitted by emit_sync.

        Args:
            sleep (float): The time to sleep between emitting events (in seconds). Default is 0.1 seconds.
        """
        while True:
            event = await self.event_queue.get()  # type: ignore
            await self.emit(event)
            await asyncio.sleep(sleep)

    async def _call_handler(self, func, event):
        res = func[0](**event)
        if isinstance(res, type_coro):
            await res
