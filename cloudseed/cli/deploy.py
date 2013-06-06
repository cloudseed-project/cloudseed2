'''
usage:
  cloudseed deploy <profile>...

options:
  -h, --help         Show this screen.
  <profile>          The state you would like to deploy
'''
import logging
from docopt import docopt
from cloudseed.utils import ssh
from cloudseed.utils import env

log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)
    cloud = env.cloud()
    profile = args['<profile>']

    # TODO ensure we have a bootstrapped master
    # bail if we don't

    client = ssh.master_client(cloud)
    ssh.sudo(client, 'salt-cloud -p %s %s' % (profile, profile))




