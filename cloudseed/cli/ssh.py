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
from cloudseed.utils import ssh


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

    provider = providers.get(profile['provider'], None)

    if not provider:
        # TODO Add Error Messaging
        return

    username = profile.get('ssh_username', False)
    identity = provider.get('private_key', False)
    host = conf.get('ip_address', False)

    if username and identity and host:
        identity = os.path.abspath(identity)
        #sys.stdout.write('Connecting to environment \'%s\'\n' % current_env)
        ssh.connect(
            host=host,
            username=username,
            identity=identity)
