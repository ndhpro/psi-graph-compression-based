from glob import glob
from utils import load_graph


paths = glob('data/psi_graph/benign/*.txt')
nodes = {}
for path in paths:
    graph = load_graph(path)
    n_node = len(graph.nodes)
    nodes[n_node] = nodes.get(n_node, 0) + 1

nodes = sorted(nodes.items())
print(nodes)
