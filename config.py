import os
import argparse
import yaml

def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str)
    args = parser.parse_args()
    with open(args.config) as f:
        config = yaml.safe_load(f)
    return config

def set_dir(path):
    if os.path.exists(path):
        return
    else:
        os.makedirs(path)
        return
