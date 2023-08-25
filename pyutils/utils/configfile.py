import json
try:
    from types import SimpleNamespace as Namespace
except ImportError:
    from argparse import Namespace

def load(config_file):
    with open(config_file, 'r') as read_file:
        return json.load(read_file, object_hook=lambda d: Namespace(**d))