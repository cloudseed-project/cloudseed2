from __future__ import absolute_import
import os
import yaml
# import saltcloud.utils.parsers
# import cloudseed.cloud


def cloudseed_conf():
    try:
        with open('cloudseed/current/salt/cloudseed') as f:
            return yaml.load(f.read())
    except IOError:
        return {}


def location_name():
    return os.path.basename(os.getcwd())


def env_name():
    return os.path.basename(env_path())


def env_path():
    return os.path.realpath(current_env_path())


def current_env_path():
    return os.path.abspath(
        os.path.join(
            os.getcwd(),
            'cloudseed',
            'current'))
