'''
usage:
  cloudseed bootstrap <environment>

options:
  <environment>         The profile name in your cloudseed/ folder to load
  -h, --help            Show this screen.

'''
import os
from cloudseed.utils import saltcloud as cs_saltcloud
from cloudseed.utils import env


def run(argv):
    prefix = os.path.join(env.current_env_path(), 'salt')

    cs_saltcloud.destroy(
        cloud_config=os.path.join(prefix, 'cloud'),
        cloud_providers=os.path.join(prefix, 'cloud.providers'),
        cloud_profiles=os.path.join(prefix, 'cloud.profiles'),
        master_config=os.path.join(prefix, 'master'))
