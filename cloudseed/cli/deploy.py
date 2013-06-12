'''
usage:
  cloudseed deploy <profile>...

options:
  -h, --help         Show this screen.
  <profile>          The state you would like to deploy
'''
import logging
from docopt import docopt
from cloudseed.utils import env
from cloudseed.agent import commands

log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)
    profile = args['<profile>'][0]

    tag = 'cloudseed-%s-%s-%s' % (env.location_name(), env.env_name(), profile)

    # TODO ensure we have a bootstrapped master
    # bail if we have not
    commands.deploy(profile, tag)
