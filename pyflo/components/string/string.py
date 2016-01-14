import pyflo.component
from collections import deque


class SplitComponent(pyflo.component.Component):
    separator = None

    def __init__(self, metadata):
        inports = {
            "in": {},
            "separator": {},
        }
        outports = {
            "out": {},
        }
        super().__init__(inports, outports)
        self.queued_input = deque()
        self.inports["in"].on("data", self.split)
        self.inports["separator"].on("data", self.set_separator)

    def split(self, data):
        # if the separator port is connected, use the value of separator or wait for it if not yet set
        if self.inports["separator"].attached():
            if self.separator is None:
                self.queued_input.append(data)
                return
            else:
                separator = self.separator
        else:
            separator = None
        self._split(data, separator)

    def _split(self, data, separator):
        split_string = data.split(separator)
        self.outports["out"].begin_group()
        for string in split_string:
            self.outports["out"].send_data(string)
        self.outports["out"].end_group()

    def set_separator(self, data):
        self.separator = str(data)
        while len(self.queued_input) > 0:
            self._split(self.queued_input.popleft(), self.separator)
