import pandas as pd
import shutil
from glob import glob
from scipy.sparse.construct import random
from tqdm import tqdm
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from sklearn.model_selection import train_test_split

RAW_PATH = 'data/raw/'
GRAPH_PATH = 'data/graphs/'


def get_ucf():
    print('Getting UCF malware samples...')
    elf_info = pd.read_csv(RAW_PATH + 'elf_v2.csv')
    malware_paths = glob(RAW_PATH + 'psi_graph_v2/malware/*')

    def get_graph(path):
        md5 = path.split('/')[-1].replace('.txt', '')
        if elf_info.loc[elf_info['md5'] == md5, 'Dataset'].values[0] == 'UCF':
            graph_path = path.replace('raw/psi_graph_v2/', 'graphs/')
            shutil.copy(path, graph_path)

    Parallel(n_jobs=cpu_count())(delayed(get_graph)(path)
                                 for path in tqdm(malware_paths))


def split_data():
    malware_paths = glob(GRAPH_PATH + 'malware/*')
    benign_paths = glob(GRAPH_PATH + 'benign/*')
    paths = malware_paths + benign_paths
    labels = len(malware_paths) * [1] + len(benign_paths) * [0]

    X_train, X_test, y_train, y_test = train_test_split(
        paths, labels, test_size=.3, random_state=42
    )

    pd.DataFrame({
        'path': X_train,
        'label': y_train
    }).to_csv('data/train.csv', index=None)
    pd.DataFrame({
        'path': X_test,
        'label': y_test
    }).to_csv('data/test.csv', index=None)


if __name__ == '__main__':
    # get_ucf()
    split_data()
