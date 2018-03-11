import sys


def call_graph_to_dot(callgraph, fd=sys.stdout):
    print("digraph callgraph {", file=fd)
    for metric, callees in callgraph.items():
        for callee, n in callees.items():
            print('\t{} -> {} [label="{}"];'.format(metric, callee, n),
                  file=fd)
    print("}", file=fd)
