from __future__ import absolute_import
import os
import yaml
import saltcloud.utils.parsers
import cloudseed.cloud


def cloudseed_conf():
    try:
        with open('cloudseed/current/salt/cloudseed') as f:
            return yaml.load(f.read())
    except IOError:
        return {}


def cloud():
    '''
    To be used in utility functions that are not part of a saltcloud run.
    This object will be available if running within bootstrap for example.
    You would need this helper though if you wanted the configuration from
    withing ssh or sync.

    Also note this uses the cloudseed extended version of
    saltcloud.cloud.Cloud
    '''
    prefix = current_env_path()

    cloudseed_args = [
    '--cloud-config', os.path.join(prefix, 'salt', 'cloud'),
    '--profiles', os.path.join(prefix, 'salt', 'cloud.profiles'),
    '--providers-config',  os.path.join(prefix, 'salt', 'cloud.providers'),
    '--master-config',  os.path.join(prefix, 'salt', 'master'),
    ]

    obj = saltcloud.utils.parsers.SaltCloudParser()
    obj.parse_args(cloudseed_args)
    obj.config['cloudseed'] = cloudseed_conf()

    return cloudseed.cloud.Cloud(obj.config)


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
