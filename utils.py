import os
import constants as c

def check_for_folders():
    # Function which 

    if not os.path.exists(c.DATA):
        os.mkdir(c.DATA)
    if not os.path.exists(c.PARQUET):
        os.mkdir(c.PARQUET)
    if not os.path.exists(c.CSV):
        os.mkdir(c.CSV)
    if not os.path.exists(c.SQLITE):
        os.mkdir(c.SQLITE)
    if not os.path.exists(c.JSONL):
        os.mkdir(c.JSONL)


def get_max_indexes(arr, n):
    # Takes in an array of floats or ints and outputs a list of the indexes where the top n values are located

    if len(arr) < n:
        return None
    c_arr = arr.copy()
    c_arr.sort()
    max_indexes = []
    for i in range(n):
        max_indexes.append(arr.index(c_arr[len(c_arr) - 1]))
        c_arr.pop(len(c_arr) - 1)
    return max_indexes

