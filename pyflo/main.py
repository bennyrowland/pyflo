import argparse
import sys
import json
import pyflo.graph


def run_graph():
    # start with a simple parser which looks for the single positional argument, the path to the graph file
    parser = argparse.ArgumentParser()
    # this argument is optional, if not supplied then we try and read the graph from stdin instead
    parser.add_argument("graph", nargs='?')
    # argument to configure possible graph loaders
    parser.add_argument("--loaders")
    file_args, remaining_args = parser.parse_known_args()
    # if graph loader config was given, create the graph loaders
    if file_args.loaders:
        loader_config = json.loads(file_args.loaders)
        pyflo.graph.configure_graph_loaders(loader_config)
    if file_args.graph:
        print("running pyflo graph in file {}".format(file_args.graph), flush=True)
        try:
            #with open(file_args.graph, 'rt') as fin:
            #    graph_spec = json.load(fin)
            graph_spec = pyflo.graph.load_graph(file_args.graph)
        except Exception as e:
            print("Error loading graph from file {}".format(file_args.graph))
            print(e)
            exit(-1)
    elif not sys.stdin.isatty():
        print("running pyflo graph piped from stdin")
        try:
            graph_spec = json.load(sys.stdin)
        except Exception as e:
            print("Error loading graph from stdin")
            print(e)
            exit(-1)
    else:
        parser.print_help()
        return

    # now the graph specification is loaded, we can parse the rest of the cli arguments which define inputs to
    # the graph
    if "inports" in graph_spec:
        inport_parser = argparse.ArgumentParser()
        for inport in graph_spec["inports"]:
            inport_parser.add_argument("--" + inport["name"])
        inport_args = vars(inport_parser.parse_args(remaining_args))
    else:
        inport_args = {}

    # run the graph with the supplied inport values
    pyflo.graph.run_graph(graph_spec, inport_args)

    exit(0)


def export_components():
    """
    Sends to stdout a JSON object describing the installed pyflo components
    :return:
    """
    from stevedore import extension

    mgr = extension.ExtensionManager(
        namespace="pyflo",
        invoke_on_load=False
    )

    extension_list = mgr.names()
    # have to remove the graph component which is special
    extension_list.remove("pyflo.core.graph")

    #def process(name, component, folder):
    #    if "." in name:
    #        sub_folder, rest = name.split(".", 1)
    #        if sub_folder not in folder["folders"]:
    #            folder["folders"][sub_folder] = {"components": {}, "folders": {}}
    #        process(rest, component, folder["folders"][sub_folder])
    #    else:
    #        folder["components"][name] = component

    def process(name, component, folder):
        if "." in name:
            subfolder_name, rest = name.split(".", 1)
            for child_folder in folder["children"]:
                if child_folder["name"] == subfolder_name:
                    process(rest, component, child_folder)
                    break
            else:
                new_folder = {"name": subfolder_name, "children": []}
                folder["children"].append(new_folder)
                process(rest, component, new_folder)
        else:
            folder["children"].append(dict({"name": name, "children": []}, **component))


    #
    component_library = {"children": []}
    for component_name in extension_list:
        # we need to make an instance of the plugin so we can find out about it
        instance = mgr[component_name].plugin({})

        # remove the first component (always "pyflo" to remove the top level of the hierarchy
        pyflo_string, component_name = component_name.split(".", 1)
        component_dict = {"id": component_name, "config": {"inports": [], "outports": []}}

        # get a list of the inports, outports and their config
        for inport_name, inport in instance.inports.items():
            component_dict["config"]["inports"].append(dict({"name": inport_name}, **inport.config))
        for outport_name, outport in instance.outports.items():
            component_dict["config"]["outports"].append(dict({"name": outport_name}, **outport.config))

        process(component_name, component_dict, component_library)

    #print(component_library)

    #print(component_library)
    import json
    print(json.dumps(component_library, indent=4))
