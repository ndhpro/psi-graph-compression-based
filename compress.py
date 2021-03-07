import networkx as nx
from math import log2
from matplotlib import pyplot as plt
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from time import time
from datetime import datetime
from glob import glob


N_JOBS = cpu_count()
SUBGRAPH_PATH = 'data/subgraphs'


def load_graph(path):
    G = nx.MultiDiGraph()
    with open(path, 'r') as f:
        lines = f.readlines()

    for line in lines[2:]:
        edge = line.split()
        if len(edge) == 2:
            G.add_edge(*edge)
    return G


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


def initial_subgraphs(G: nx.MultiDiGraph):
    subgraphs = []
    for node in G.nodes:
        succ = list(G.successors(node))
        if len(succ) > 1 or (len(succ) == 1 and succ[0] != node):
            subgraphs.append(node)
    return sorted(subgraphs)


def get_best(G: nx.MultiDiGraph, best_subgraphs, new_subgraphs):
    def cal_MDL(sg):
        nodes = sg.split()
        dl = MDL(G, G.subgraph(nodes))
        return (sg, dl)

    new_subgraphs = Parallel(n_jobs=N_JOBS)(
        delayed(cal_MDL)(sg) for sg in new_subgraphs)

    best_subgraphs.extend(new_subgraphs)

    best_subgraphs = sorted(best_subgraphs, key=lambda k: k[1])[:20]
    new_subgraphs = sorted(new_subgraphs, key=lambda k: k[1])[:20]
    subgraphs = [k[0] for k in new_subgraphs]

    return best_subgraphs, subgraphs


def run(G: nx.MultiDiGraph):
    best_subgraphs = []
    subgraphs = []
    the_best = None
    t = time()

    for _ in range(10):
        new_subgraphs = set()
        if not best_subgraphs:
            new_subgraphs = initial_subgraphs(G)
        else:
            for sg in subgraphs:
                succs = set()
                for node in sg.split():
                    succs.update(G.successors(node))
                for node in succs:
                    if node not in sg.split() and not node.startswith('_'):
                        new_sg = ' '.join(sorted(sg.split() + [node]))
                        new_subgraphs.add(new_sg)

        best_subgraphs, subgraphs = get_best(G, best_subgraphs, new_subgraphs)
        if not best_subgraphs:
            return G, time()-t

        nodes = best_subgraphs[0][0].split()
        the_best = G.subgraph(nodes)

        if not subgraphs or time()-t > 60:
            break

    # plt.figure()
    # nx.draw(the_best, with_labels=True)
    # plt.savefig('best_subgraph.png')
    return the_best, time()-t


if __name__ == '__main__':
    graph_paths = sorted(glob('data/psi_graph/benign/*.txt'))[2000:]

    for path in graph_paths:
        subgraph_path = path.replace(
            'psi_graph', 'subgraphs').replace('.txt', '.edgelist')
        if glob(subgraph_path):
            continue

        print(path)
        G = load_graph(path)
        the_best, t = run(G)
        print(' '.join(the_best.nodes))
        print('%.2f\n' % t)

        nx.write_edgelist(the_best, subgraph_path + ".edgelist")
