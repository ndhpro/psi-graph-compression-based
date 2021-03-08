import os
from glob import glob


paths = glob('data/subgraphs/benign/*.edgelist.edgelist')
print(len(paths))
for path in paths:
    os.rename(path, path.replace('.edgelist.edgelist', '.edgelist'))
