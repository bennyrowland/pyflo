class Port:
    def __init__(self, config):
        self.config = config


class Inport(Port):
    """

    """

    def __init__(self, config):
        super().__init__(config)
        self.outports = set()
        self._events = {
            "connect": [],
            "beginGroup": [],
            "data": [],
            "disconnect": [],
            "endGroup": [],
        }

    def on(self, event_name, function=None):
        """
        Sets a function to be called when the port receives an event. This function can be used in two ways: directly by
        passing in an existing function or as a decorator for a newly defined function.
        :param event_name: The name of the event to which the function should be attached
        :param function: The function to call when the event occurs
        :return:
        """
        def _on(func):
            if event_name not in self._events:
                raise KeyError("Inport does not accept {} events".format(event_name))
            if func not in self._events[event_name]:
                self._events[event_name].append(func)
            return func

        if function is None:
            # if function is not provided this is a decorator call
            return _on
        else:
            # this is a standard function call
            return _on(function)

    def on_connect(self, outport):
        self.outports.add(outport)
        for function in self._events["connect"]:
            function()

    def disconnect(self, outport):
        if outport in self.outports:
            self.outports.remove(outport)
            for function in self._events["disconnect"]:
                function()

    def attached(self):
        return len(self.outports) > 0

    def data(self, data):
        for function in self._events["data"]:
            function(data)

    def begin_group(self):
        for function in self._events["beginGroup"]:
            function()

    def end_group(self):
        for function in self._events["endGroup"]:
            function()


class Outport(Port):
    def __init__(self, config):
        super().__init__(config)
        self.listeners = set()

    def connect(self, inport):
        self.listeners.add(inport)
        inport.on_connect(self)

    def send_data(self, data):
        for listener in self.listeners:
            listener.data(data)

    def disconnect(self):
        for listener in self.listeners:
            listener.disconnect(self)
            #listener.disconnect()
        self.listeners = set()

    def begin_group(self):
        for listener in self.listeners:
            listener.begin_group()

    def end_group(self):
        for listener in self.listeners:
            listener.end_group()


class PassThroughPort(Inport):
    """
    The PassThroughPort behaves like both an inport and an outport, it is used inside the Graph component to provide a
    port that can act as an intermediary between the outside network and the processes inside the graph. One issue is
    that connections between the PassThroughPort and internal inports should not be "connected" unless the
    PassThroughPort also has a connection from outside the network.
    """
    def __init__(self, config):
        super().__init__(config)
        self.outport = Outport(config)
        self.on("data", self.pass_data)
        self.on("beginGroup", self.outport.begin_group)
        self.on("endGroup", self.outport.end_group)
        self.on("connect", self.make_connections)
        self.target_inports = set()

    def connect(self, inport):
        self.target_inports.add(inport)
        if self.attached():
            self.make_connections()

    def make_connections(self):
        for inport in self.target_inports:
            self.outport.connect(inport)

    def pass_data(self, data):
        self.outport.send_data(data)
