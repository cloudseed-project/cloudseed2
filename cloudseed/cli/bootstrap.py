'''
usage:
  cloudseed bootstrap <environment>

options:
  <environment>         The profile name in your cloudseed/ folder to load
  -h, --help            Show this screen.

'''
import os
from cloudseed.utils import saltcloud
from cloudseed.utils import env


def run(argv):
    tag = 'cloudseed-%s-%s-master' % (env.location_name(), env.env_name())
    prefix = os.path.join(env.current_env_path(), 'salt')

    saltcloud.execute_profile(
        'master',
        tag=tag,
        cloud_config=os.path.join(prefix, 'cloud'),
        cloud_providers=os.path.join(prefix, 'cloud.providers'),
        cloud_profiles=os.path.join(prefix, 'cloud.profiles'),
        master_config=os.path.join(prefix, 'master'))

