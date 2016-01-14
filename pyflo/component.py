import pyflo.ports


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
