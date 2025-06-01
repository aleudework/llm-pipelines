import yaml

def load_config(path: str):
    """
    Loads yaml file based on a path
    """
    with open(path, "r") as f:
        return yaml.safe_load(f)
