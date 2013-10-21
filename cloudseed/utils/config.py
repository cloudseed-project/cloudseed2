import os
from confypy import Config
from confypy import Location

_cached_config = None


def load_config():
    global _cached_config

    if _cached_config:
        return _cached_config

    local_settings = os.path.join(os.getcwd(), '.cloudseed')

    defaults = {
    'boxes_url': 'https://raw.github.com/cloudseed-project/cloudseed-data/master/boxes.yaml',
    'ports_url': 'https://raw.github.com/cloudseed-project/cloudseed-data/master/ports.yaml'
    }

    config = Config(chain=True, defaults=defaults)
    config.locations = [
        Location.from_env_path('CLOUDSEED_SETTINGS', parser='yaml'),
        Location.from_path(local_settings, parser='yaml')
    ]

    _cached_config = config.data

    return config.data
