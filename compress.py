import networkx as nx
from glob import glob
from math import log2, inf
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from utils import load_graph
from matplotlib import pyplot as plt

N_JOBS = cpu_count()


def length(G: nx.MultiDiGraph):
    n = len(G.nodes)
    e = len(G.edges)
    if n == 0:
        return 0
    else:
        return n*log2(n) + e*2*log2(n)


def MDL(G: nx.MultiDiGraph, nodes):
    H = nx.MultiDiGraph()
    K = nx.MultiDiGraph()
    for (u, v, _) in G.edges:
        if u in nodes and v in nodes:
            H.add_edge(u, v)
        elif u in nodes and v not in nodes:
            K.add_edge(' ', v)
        elif u not in nodes and v in nodes:
            K.add_edge(u, ' ')
        else:
            K.add_edge(u, v)

    return length(H) + length(K)


def compress(path):
    G = load_graph(path)
    pattern_path = path.replace('psi_graph', 'patterns')
    if glob(pattern_path):
        return

    patterns = G.nodes()
    best_pattern = ['', inf]

    for _ in range(9):
        new_patterns = set()
        for sg in patterns:
            nodes = sg.split()
            succs = set()
            for node in nodes:
                succs.update(G.successors(node))
            for node in succs:
                if node not in nodes:
                    new_sg = ' '.join(sorted(nodes + [node]))
                    new_patterns.add(new_sg)

        if not new_patterns:
            break

        tmp = []
        for sg in new_patterns:
            nodes = sg.split()
            score = MDL(G, nodes)
            tmp.append((sg, score))
        new_patterns = sorted(tmp, key=lambda k: k[1])
        patterns = [k[0] for k in new_patterns[:10]]
        if best_pattern[1] > new_patterns[0][1]:
            best_pattern = new_patterns[0]
        else:
            break

    print(best_pattern)
    best_pattern = nx.DiGraph(G.subgraph(best_pattern[0].split()))
    nx.write_edgelist(best_pattern, pattern_path)

    # nx.draw(best_pattern, with_labels=True)
    # plt.savefig('img/bashlite.png', dpi=300)


if __name__ == '__main__':
    graph_paths = sorted(glob('data/psi_graph/benign/*.txt'))
    Parallel(n_jobs=N_JOBS, verbose=100)(delayed(compress)(path)
                                         for path in graph_paths)
    # compress(graph_paths[0])
