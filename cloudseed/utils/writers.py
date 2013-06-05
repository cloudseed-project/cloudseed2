import logging
import yaml

log = logging.getLogger(__name__)


def write_yaml(filename, data):
    encoded = yaml.safe_dump(data, default_flow_style=False)

    try:
        with open(filename, 'w') as f:
            f.write(encoded)
    except IOError:
        log.error('Failed writing file %s with %s', filename, data)
        raise


def write_string(filename, data):
    try:
        with open(filename, 'w') as f:
            f.write(data)
    except IOError:
        log.error('Failed writing file %s with %s', filename, data)
        raise
