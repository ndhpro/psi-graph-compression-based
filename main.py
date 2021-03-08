import sys
import networkx as nx
import pandas as pd
from glob import glob
from sklearn.model_selection import train_test_split
from Graph2vec import Graph2vec
from Classifiers import Classifiers
from tqdm import tqdm
from joblib import dump, load

NODE_PATH = 'data/nodes.joblib'
paths = glob(f'data/subgraphs/*/*.edgelist')
labels = [0 if 'benign' in path else 1 for path in paths]
path_train, path_test, y_train, y_test = train_test_split(
    paths, labels, test_size=0.3, random_state=28
)


def get_nodes():
    nodes = set()
    for path in tqdm(path_train):
        graph = nx.read_edgelist(path)
        nodes.update(graph.nodes)
    nodes = list(nodes)
    node_dic = {}
    for n in nodes:
        node_dic[n] = nodes.index(n)
    dump(node_dic, NODE_PATH)


def vectorize():
    nodes = load(NODE_PATH)
    graph2vec = Graph2vec(
        nodes=nodes,
    )

    embeddings = graph2vec.train(path_train)
    embeddings.to_csv('data/train.csv', index=None)

    # graph2vec.load_model()
    embeddings = graph2vec.apply(path_test)
    embeddings.to_csv('data/test.csv', index=None)


if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'node':
        get_nodes()
    elif command == 'vectorize':
        vectorize()

    elif command == 'classify':
        train = pd.read_csv('data/train.csv')
        test = pd.read_csv('data/test.csv')
        X_train = train.loc[:, 'x_0':].values
        X_test = test.loc[:, 'x_0':].values

        classifiers = Classifiers(
            # algo=['KNN', 'DT'],
            model_path='models/'
        )
        classifiers.run(X_train, X_test, y_train, y_test)
