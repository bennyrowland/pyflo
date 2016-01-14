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
        print("running pyflo graph in file {}".format(file_args.graph))
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
