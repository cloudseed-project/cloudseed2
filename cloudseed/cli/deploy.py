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
from cloudseed.agent import commands

log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)
    cloud = env.cloud()
    profile = args['<profile>'][0]

    # TODO ensure we have a bootstrapped master
    # bail if we don't
    commands.deploy(profile, '%s0' % profile)
