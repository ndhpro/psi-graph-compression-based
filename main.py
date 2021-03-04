import networkx as nx
from math import log2
# from matplotlib import pyplot as plt
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from time import time
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
    for edge in G.edges:
        u, v, _ = edge
        if u in H.nodes and v not in H.nodes:
            K.add_edge(' ', v)
        if u not in H.nodes and v in H.nodes:
            K.add_edge(u, ' ')

    return length(H) + length(K)


def init_subgraphs(G: nx.MultiDiGraph):
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

    best_subgraphs = sorted(best_subgraphs, key=lambda k: k[1])[:50]
    new_subgraphs = sorted(new_subgraphs, key=lambda k: k[1])[:50]
    subgraphs = [k[0] for k in new_subgraphs]

    return best_subgraphs, subgraphs


def compression_rate(G: nx.MultiDiGraph, H: nx.MultiDiGraph):
    n_rate = len(H.nodes) / len(G.nodes)
    e_rate = len(H.edges) / len(G.edges)
    return 2 / (1/n_rate + 1/e_rate)


def run(G: nx.MultiDiGraph):
    t = time()
    best_subgraphs = []
    subgraphs = init_subgraphs(G)
    the_best = None

    while True:
        new_subgraphs = set()
        for sg in subgraphs:
            succs = set()
            for node in sg.split():
                succs.update(G.successors(node))
            for node in succs:
                new_sg = ' '.join(sorted(sg.split() + [node]))
                new_subgraphs.add(new_sg)

        best_subgraphs, subgraphs = get_best(G, best_subgraphs, new_subgraphs)

        if the_best and compression_rate(G, the_best) > 0.1:
            break
        else:
            the_best = G.subgraph(best_subgraphs[0][0].split())

        if not subgraphs or time()-t > 20:
            break

    # plt.figure()
    # nx.draw(the_best, with_labels=True)
    # plt.savefig('best_subgraph.png')
    return the_best, time()-t


if __name__ == '__main__':
    graph_paths = glob('data/graphs/malware/*.txt')[:5000]
    print(len(graph_paths))

    for path in graph_paths:
        print(path)
        G = load_graph(path)
        the_best, t = run(G)
        print(the_best.nodes, '%.2f' % t)

        subgraph_path = path.replace(
            'graphs', 'subgraphs').replace('.txt', '.gexf')
        nx.write_gexf(the_best, subgraph_path)
