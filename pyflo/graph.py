import pyflo.ports
import json
from types import SimpleNamespace, MappingProxyType
import pycouchdb
import pycouchdb.exceptions

from stevedore import extension

loader_manager = extension.ExtensionManager(
    namespace="pyflo.loaders",
    invoke_on_load=False
)
loader_list = []

import pkg_resources
for ep in pkg_resources.iter_entry_points("loaders"):
    print(ep)

mgr = extension.ExtensionManager(
    namespace="pyflo",
    invoke_on_load=False
)

print(mgr.names())
print(loader_manager.names())


def run_graph(graph_spec, inport_args):
    graph = Graph(graph_spec)
    graph.run(inport_args)


class Graph:
    def __init__(self, specification):
        self.processes = {}
        for process_id, config in specification["processes"].items():
            component_name = "pyflo." + config["component"]
            if component_name in mgr:
                if "metadata" in config:
                    metadata = config["metadata"]
                else:
                    metadata = {}
                self.processes[process_id] = mgr[component_name].plugin(metadata)
            else:
                raise KeyError("Component {} is not installed".format(component_name))
        # also create dummy processes for the inports and outports
        self.processes["inports"] = SimpleNamespace()
        self.processes["outports"] = SimpleNamespace()
        self.processes["inports"].outports = {}
        self.processes["outports"].inports = {}
        self.processes["inports"].graph_loaded = lambda *args: None
        self.processes["outports"].graph_loaded = lambda *args: None
        if "inports" in specification:
            for inport_config in specification["inports"]:
                self.processes["inports"].outports[inport_config["name"]] = pyflo.ports.PassThroughPort(inport_config)
        if "outports" in specification:
            for outport_config in specification["outports"]:
                self.processes["outports"].inports[outport_config["name"]] = pyflo.ports.PassThroughPort(outport_config)
        for connection_data in specification["connections"]:
            target_component = self.processes[connection_data["tgt"]["process"]]
            # is this a data connection or a normal one
            if "src" in connection_data:
                start_component = self.processes[connection_data["src"]["process"]]
                start_port = start_component.outports[connection_data["src"]["port"]]
                start_port.connect(target_component.inports[connection_data["tgt"]["port"]])
            else:
                target_component.inports[connection_data["tgt"]["port"]].on_connect("data")
                target_component.inports[connection_data["tgt"]["port"]].data(connection_data["data"])

    def run(self, inport_args=MappingProxyType({})):
        # first we have to loop over all the inport args to actually connect them to the true inports
        # we only do this for the ones supplied here so they aren't connected by default
        for arg, value in inport_args.items():
            if arg in self.processes["inports"].outports and value is not None:
                self.processes["inports"].outports[arg].make_connections()
        # now all the ports know whether they are connected or not, we can send the actual data in
        for arg, value in inport_args.items():
            if arg in self.processes["inports"].outports and value is not None:
                self.processes["inports"].outports[arg].data(value)
        for process in self.processes.values():
            process.graph_loaded()


def configure_graph_loaders(config):
    print("configuring graph_loaders {}".format(config))
    for loader_name, loader_config in config.items():
        if loader_name in loader_manager:
            loader_list.append(loader_manager[loader_name].plugin(loader_config))


def load_graph(graph):

    # if no loaders have been configured, just try using the filename directly
    if len(loader_list) == 0:
        with open(graph, "rt") as fin:
            return json.load(fin)
    for loader in loader_list:
        graph_spec = loader.load_graph(graph)
        if graph_spec is not None:
            return graph_spec
    raise FileNotFoundError("Could not load graph {}".format(graph))
