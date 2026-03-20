import os
import constants as c

def check_for_folders():
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
    