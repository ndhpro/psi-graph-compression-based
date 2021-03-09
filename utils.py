import networkx as nx


def load_graph(path):
    graph = nx.MultiDiGraph()
    with open(path, 'r') as f:
        lines = f.readlines()

    for line in lines[2:]:
        edge = line.split()
        if len(edge) == 2:
            graph.add_edge(*edge)
    return graph


def is_encoded(graph):
    for node in graph.nodes:
        if node.startswith('sub_'):
            return True
    return False
