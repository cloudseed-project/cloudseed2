'''
usage:
  cloudseed deploy <profile> [--local]

options:
  -h, --help         Show this screen.
  --local            Run deploy from the current machine
  <profile>          The state you would like to deploy
'''
import logging
from docopt import docopt
from cloudseed.utils import env
from cloudseed.agent import commands
import cloudseed.agent.actions

log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)
    profile = args['<profile>']
    tag = 'cloudseed-%s-%s-%s' % (env.location_name(), env.env_name(), profile)

    # TODO ensure we have a bootstrapped master
    # bail if we have not
    if args.get('--local', False):
        cloudseed.agent.actions.execute_profile(profile, tag)
    else:
        commands.deploy(profile, tag)
