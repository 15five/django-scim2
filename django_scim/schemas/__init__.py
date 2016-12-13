import os
import json


SCHEMAS_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_SUB_DIRS = ('core', 'extension')


def load_schemas():
    schemas = []
    for dir_ in SCHEMA_SUB_DIRS:
        sub_dir = os.path.join(SCHEMAS_DIR, dir_)
        files = os.listdir(sub_dir)
        files = [os.path.join(sub_dir, f) for f in files if f.lower().endswith('.json')]
        for file_ in files:
            with open(file_) as fp:
                schemas.append(json.load(fp))

    return schemas

ALL = load_schemas()

