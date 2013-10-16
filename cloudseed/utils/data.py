import requests
import yaml
from .config import load_config


def fetch_ports():
    config = load_config()
    return fetch_yaml(config.ports_url)


def fetch_boxes():
    config = load_config()
    return fetch_yaml(config.boxes_url)


def fetch_yaml(url):
    r = requests.get(url)
    return yaml.load(r.text)

