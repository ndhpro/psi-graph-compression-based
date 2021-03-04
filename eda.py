from glob import glob
import pandas as pd
from tqdm import tqdm


def get_node_freq():
    train = pd.read_csv('data/train.csv')
    paths = train.loc[train['label'] == 1, 'path'].values

    nodes = dict()
    for path in tqdm(paths):
        with open(path, 'r') as f:
            lines = f.readlines()
        for line in lines[2:]:
            edges = line.split()
            if len(edges) == 2:
                nodes[edges[0]] = nodes.get(edges[0], 0) + 1
                nodes[edges[1]] = nodes.get(edges[1], 0) + 1

    sorted_nodes = sorted(nodes.items(), key=lambda x: x[1], reverse=True)
    pd.DataFrame(sorted_nodes).to_csv('data/node_freq_e.txt',
                                      index=None, header=['node', 'freq'])


if __name__ == '__main__':
    get_node_freq()
