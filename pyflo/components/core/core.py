import pyflo
import json


class CountingComponent(pyflo.component.Component):
    def __init__(self, metadata):
        inports = {
            "in": {},
        }
        outports = {
            "sum": {},
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
        import time
        #time.sleep(4)
        self.outports["sum"].send_data(self.count)


class GraphComponent(pyflo.component.Component):
    def __init__(self, metadata):
        super().__init__({}, {})
        # metadata should contain the graph file to load
        graph_filename = metadata["graph"]
        #with open(graph_filename, 'rt') as fin:
        #    graph_spec = json.load(fin)
        graph_spec = pyflo.graph.load_graph(graph_filename)
        self.graph = pyflo.graph.Graph(graph_spec)
        self.inports = self.graph.processes["inports"].outports
        self.outports = self.graph.processes["outports"].inports
        self.graph.run()
