import networkx as nx
import pandas as pd
from glob import glob
from joblib import dump
from utils import load_graph
from karateclub import Graph2Vec
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


def largest_cc(psi_path):
    graph = load_graph(psi_path)
    nodes = max(nx.weakly_connected_components(graph), key=len)
    cc = graph.subgraph(nodes)
    return nx.Graph(cc)


print('Load graphs...')
paths = glob('data/patterns/*/*.txt')
graphs = []
labels = [0 if 'benign' in path else 0 for path in paths]
for path in paths:
    graph = nx.read_edgelist(path)
    if len(graph) < 5:
        psi_path = path.replace('patterns', 'psi_graph')
        graph = largest_cc(psi_path)
    mapping = dict(zip(graph, range(len(graph))))
    graph = nx.relabel_nodes(graph, mapping)
    graphs.append(graph)

print('Performing Graph2vec...')
graph2vec = Graph2Vec()
graph2vec.fit(graphs)
graphs = graph2vec.get_embedding()

dump(graphs, 'data/graphs.joblib')
dump(labels, 'data/labels.joblib')
