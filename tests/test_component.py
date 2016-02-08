import pyflo
import json
from unittest.mock import patch


class InputComponent(pyflo.component.Component):
    def __init__(self):
        outports = {
            "out": {},
        }
        super().__init__({}, outports)

    def graph_loaded(self):
        self.outports["out"].send_data("test data 123 la la la")


class CountingComponent(pyflo.component.Component):
    def __init__(self):
        inports = {
            "in": {},
        }
        outports = {
            "out": {},
        }
        super().__init__(inports, outports)
        self.inports["in"].on("data", self.data)
        self.inports["in"].on("beginGroup", self.begin_group)
        self.inports["in"].on("endGroup", self.end_group)
        self.count = 0

    def begin_group(self):
        self.count = 0

    def data(self, data):
        self.count += 1

    def end_group(self):
        self.outports["out"].send_data("Counted {} components".format(self.count))


class LoggingComponent(pyflo.component.Component):
    def __init__(self):
        inports = {
            "in": {},
        }
        super().__init__(inports, {})

        self.inports["in"].on("data", self.log)

    def log(self, data):
        print(data)


@patch.object(LoggingComponent, 'log')
def test_simple(mock_method):
    start = InputComponent()
    split = pyflo.components.string.SplitComponent(None)
    count = CountingComponent()
    end = LoggingComponent()
    start.outports["out"].connect(split.inports["in"])
    split.outports["out"].connect(count.inports["in"])
    count.outports["out"].connect(end.inports["in"])
    start.graph_loaded()
    mock_method.assert_called_once_with("Counted 6 components")


def test_graph_in_graph():
    with open("pyflo/tests/graph_network.json", 'rt') as fin:
        graph_spec = json.load(fin)
    graph = pyflo.graph.Graph(graph_spec)
    graph.run()

#if __name__ == "__main__":
    #test_graph_in_graph()