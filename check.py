import os
import networkx as nx
from glob import glob
from compress import load_graph
from tqdm import tqdm
from joblib import Parallel, delayed
from multiprocessing import cpu_count


paths = glob('data/psi_graph/benign/*.txt')


def check(path):
    global count
    graph = load_graph(path)
    sg_path = path.replace('psi_graph', 'subgraphs').replace(
        '.txt', '.edgelist')
    if not os.path.exists(sg_path):
        return 0
    sg = nx.read_edgelist(sg_path, create_using=nx.MultiDiGraph)

    if len(graph.nodes) == len(sg.nodes):
        os.remove(sg_path)
        return 1
    else:
        return 0


output = Parallel(n_jobs=cpu_count())(delayed(check)(path)
                                      for path in tqdm(paths))
print(sum(output))
