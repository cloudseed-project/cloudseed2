import requests
import yaml
from .config import load_config
from . import filesystem


def fetch_ports():
    config = load_config()
    return fetch_yaml(config.ports_url)


def fetch_boxes():
    config = load_config()
    return fetch_yaml(config.boxes_url)


def fetch_yaml(url):
    import pdb; pdb.set_trace()
    if url.startswith('http://') or \
       url.startswith('https://'):
        r = requests.get(url)
        data = r.text
    else:
        data = filesystem.read_file(url)

    return yaml.load(data)

