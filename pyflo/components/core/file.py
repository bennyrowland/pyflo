import pyflo


class FileReadComponent(pyflo.component.Component):
    def __init__(self, metadata):
        inports = {
            "source": {}
        }
        outports = {
            "out": {}
        }
        super().__init__(inports, outports)
        self.inports["source"].on("data", self.load_file)

    def load_file(self, data):
        with open(data, "rt") as fin:
            text = fin.read()
        self.outports["out"].send_data(text)

    #def graph_loaded(self):
    #    with open("/home/ben/Documents/dal makhani.txt", "rt") as fin:
    #        text = fin.read()
    #    self.outports["out"].send_data(text)


class ConsoleLoggerComponent(pyflo.component.Component):
    def __init__(self, metadata):
        inports = {
            "in": {},
        }
        super().__init__(inports, {})
        self.inports["in"].on("data", lambda x: print("{}".format(x), flush=True))
