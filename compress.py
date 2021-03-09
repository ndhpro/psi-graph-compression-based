import networkx as nx
from glob import glob
from math import log2
from joblib import Parallel, delayed
from multiprocessing import cpu_count

from networkx.algorithms.centrality import load
from utils import load_graph

N_JOBS = cpu_count()


def MDL(G: nx.MultiDiGraph, H: nx.MultiDiGraph):
    def length(G: nx.MultiDiGraph):
        n = len(G.nodes)
        e = len(G.edges)
        return n*log2(n) + e*2*log2(n)

    K = nx.MultiDiGraph(G)
    K.remove_nodes_from(H.nodes)
    K.remove_edges_from(H.edges)

    K.add_node(' ')
    for node in H.nodes:
        for succ in G.successors(node):
            if succ not in H.nodes:
                K.add_edge(' ', succ)
        for pred in G.predecessors(node):
            if pred not in H.nodes:
                K.add_edge(pred, ' ')

    return length(H) + length(K)


def process_patterns(G: nx.MultiDiGraph, best_patterns, new_patterns):
    patterns = []
    for sg in new_patterns:
        nodes = sg.split()
        mdl = MDL(G, G.subgraph(nodes))
        patterns.append((sg, mdl))

    patterns = sorted(patterns, key=lambda k: k[1])
    best_patterns.extend(patterns[:20])
    patterns = [k[0] for k in patterns[:20]]

    return best_patterns, patterns


def compress(path):
    print(path)
    G = load_graph(path)
    pattern_path = path.replace('psi_graph', 'patterns')
    if glob(pattern_path):
        return

    best_patterns = []
    patterns = G.nodes()

    for _ in range(4):
        new_patterns = set()

        for sg in patterns:
            nodes = sg.split()
            succs = set()
            for node in nodes:
                succs.update(G.successors(node))
            for node in succs:
                if node not in nodes and not node.startswith('_'):
                    new_sg = ' '.join(sorted(nodes + [node]))
                    new_patterns.add(new_sg)

        best_patterns, patterns = process_patterns(
            G, best_patterns, new_patterns)
        if not patterns:
            break

    with open(pattern_path, 'w') as f:
        for pattern in best_patterns:
            f.write(pattern[0] + '\n')


if __name__ == '__main__':
    graph_paths = glob('data/psi_graph/bashlite/*.txt')
    Parallel(n_jobs=N_JOBS, verbose=100)(delayed(compress)(path)
                                         for path in graph_paths)
