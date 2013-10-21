import os
from confypy import Config
from confypy import Location

CONFIG = None


def load_config(**kwargs):
    global CONFIG

    if CONFIG:
        return CONFIG

    local_settings = os.path.join(os.getcwd(), '.cloudseed')

    defaults = {
    'boxes_url': 'https://raw.github.com/cloudseed-project/cloudseed-data/master/boxes.yaml',
    'ports_url': 'https://raw.github.com/cloudseed-project/cloudseed-data/master/ports.yaml'
    }

    config = Config(chain=True, defaults=defaults)
    config.locations = [
        Location.from_env_path('CLOUDSEED_SETTINGS', parser='yaml'),
        Location.from_path(local_settings, parser='yaml'),
        Location.from_dict(kwargs)
    ]

    CONFIG = config.data

    return config.data
