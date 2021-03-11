import networkx as nx
import pandas as pd
from glob import glob
from joblib import dump, load
from utils import load_graph
from karateclub import Graph2Vec
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Normalizer, StandardScaler
from imblearn.over_sampling import SMOTE
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

paths = glob('data/patterns/*/*.txt')


def largest_cc(psi_path):
    graph = load_graph(psi_path)
    nodes = max(nx.weakly_connected_components(graph), key=len)
    cc = graph.subgraph(nodes)
    return nx.Graph(cc)


print('Load graphs...')
graphs = []
labels = []
for path in paths:
    graph = nx.read_edgelist(path)
    if len(graph) < 10:
        psi_path = path.replace('patterns', 'psi_graph')
        graph = largest_cc(psi_path)
    mapping = dict(zip(graph, range(len(graph))))
    graph = nx.relabel_nodes(graph, mapping)
    graphs.append(graph)
    if 'benign' in path:
        labels.append(0)
    else:
        labels.append(1)

print('Performing Graph2vec...')
graph2vec = Graph2Vec()
graph2vec.fit(graphs)
graphs = graph2vec.get_embedding()

dump(graphs, 'data/graphs.joblib')
dump(labels, 'data/labels.joblib')
graphs = load('data/graphs.joblib')
labels = load('data/labels.joblib')

print(len(graphs), len(labels))

X_train, X_test, y_train, y_test = train_test_split(
    graphs, labels, test_size=.3, random_state=42
)

smote = SMOTE()
smote.fit_resample(X_train, y_train)

normalizer = StandardScaler()
X_train = normalizer.fit_transform(X_train, y_train)
X_test = normalizer.transform(X_test)

estimator = RandomForestClassifier(n_jobs=-1)
estimator.fit(X_train, y_train)
y_pred = estimator.predict(X_test)
report = classification_report(y_test, y_pred, digits=4)
print(report)
