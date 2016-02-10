import pyflo.ports

from collections import deque


def wait_for(parameter):
    def wrap(f):
        def wrapped_function(self, data):
            param_value = None
            if self.inports[parameter].attached():
                if getattr(self, parameter) is None:
                    if not hasattr(self, "queued_input"):
                        self.queued_input = deque()
                    self.queued_input.append({"data": data, "func": f})
                    return
                else:
                    param_value = getattr(self, parameter)
            f(self, data, param_value)
        return wrapped_function
    return wrap


def empty_queue(f):
    def wrapped_function(self, data):
        f(self, data)
        if hasattr(self, 'queued_input'):
            while len(self.queued_input) > 0:
                item = self.queued_input.popleft()
                item["func"](self, item["data"], data)
    return wrapped_function


class Component:
    def __init__(self, inports, outports):
        self.inports = {}
        for name, config in inports.items():
            self.inports[name] = pyflo.ports.Inport(config)
        self.outports = {}
        for name, config in outports.items():
            self.outports[name] = pyflo.ports.Outport(config)

    def graph_loaded(self):
        pass


#def createWirePatternComponent(wireInports, ):
#    pass
