import networkx as nx
from glob import glob
from sklearn.model_selection import train_test_split

seed = 42


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


def split_data():
    paths = glob('data/psi_graph/*/*')
    labels = [0 if 'benign' in path else 0 for path in paths]

    train_paths, test_paths, y_train, y_test = train_test_split(
        paths, labels, test_size=0.3, random_state=seed
    )
    return train_paths, test_paths, y_train, y_test
