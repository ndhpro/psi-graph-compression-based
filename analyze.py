import os
import networkx as nx
from glob import glob
from utils import is_encoded, load_graph


# paths = glob('data/patterns/benign/*')
# nodes = {}
# encoded = 0
# encoded_nodes = {}
# for path in paths:
#     graph = nx.read_edgelist(path)
#     n_node = len(graph.nodes)
#     nodes[n_node] = nodes.get(n_node, 0) + 1
#     if is_encoded(graph):
#         encoded += 1
#         encoded_nodes[n_node] = encoded_nodes.get(n_node, 0) + 1

# nodes = sorted(nodes.items())
# encoded_nodes = sorted(encoded_nodes.items())
# print(f'{nodes=}')
# print(f'{encoded=}')
# print(f'{encoded_nodes=}')

paths = glob('data/psi_graph/*/*.txt')
for path in paths:
    graph = load_graph(path)
    if not graph:
        print(path)
        pattern_path = path.replace('psi_graph', 'patterns')
        os.remove(pattern_path)
