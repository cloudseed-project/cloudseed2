'''
usage:
  cloudseed ssh

options:
  -h, --help               Show this screen.
'''
import os
import logging
from docopt import docopt
import yaml
import saltcloud.cli
import saltcloud.config as config
from cloudseed.utils import ssh
from cloudseed.utils import env
import cloudseed.cloud


log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)

    # TODO We can capture all this loading and error handling
    # in 1 function
    try:
        with open('cloudseed/current/salt/cloud.profiles') as f:
            profiles = yaml.load(f.read())
    except IOError:
        print('No Cloud Profiles Found')
        return

    try:
        with open('cloudseed/current/salt/cloud.providers') as f:
            providers = yaml.load(f.read())
    except IOError:
        print('No Cloud Providers Found')
        return

    try:
        with open('cloudseed/current/salt/cloudseed') as f:
            conf = yaml.load(f.read())
    except IOError:
        print('Have you bootstrapped?')
        return

    profile = profiles.get('master', None)

    if not profile:
        # TODO Add Error Messaging
        return

    prefix = os.path.join(env.current_env_path(), 'salt')
    cloud_config = os.path.join(prefix, 'cloud')
    cloud_providers = os.path.join(prefix, 'cloud.providers')
    cloud_profiles = os.path.join(prefix, 'cloud.profiles')
    master_config = os.path.join(prefix, 'master')

    cloudseed_args = [
    '--cloud-config', cloud_config,
    '--providers-config', cloud_providers,
    '--profiles', cloud_profiles,
    '--master-config', master_config]

    cli = saltcloud.cli.SaltCloud()
    cli.parse_args(args=cloudseed_args)

    cloud = cloudseed.cloud.Cloud(cli.config)
    vm_ = cloud.vm_profile('master')

    provider = config.get_config_value(
        'provider',
        vm_,
        cloud.opts)

    if not provider:
        # TODO Add Error Messaging
        return

    username = config.get_config_value('ssh_username', vm_, cloud.opts)
    identity = config.get_config_value('private_key', vm_, cloud.opts)
    host = conf.get('ip_address', False)

    if username and identity and host:
        identity = os.path.abspath(identity)
        #sys.stdout.write('Connecting to environment \'%s\'\n' % current_env)
        ssh.connect(
            host=host,
            username=username,
            identity=identity)
