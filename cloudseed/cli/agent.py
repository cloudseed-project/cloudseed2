'''
usage:
  cloudseed agent [<action>] [-d|--daemonize]

options:
  -h, --help         Show this screen.
  -d --daemonize     Daemonize
  <action>           One of (listen|worker|events)
'''
import logging
import subprocess
from docopt import docopt
from cloudseed.agent import main

log = logging.getLogger(__name__)


def run(argv):
    # this needs some rethinking
    args = docopt(__doc__, argv=argv)

    if args['<action>']:
        actions = {
        'listen': main.cloudseed_agent,
        'worker': main.cloudseed_worker,
        'events': main.cloudseed_events
        }

        command = actions.get(args['<action>'], False)

        if command:
            command(daemon=args.get('--daemonize', False))
    else:
        subprocess.Popen(['cloudseed', 'agent', 'listen', '-d'])
        subprocess.Popen(['cloudseed', 'agent', 'worker', '-d'])
        subprocess.Popen(['cloudseed', 'agent', 'events', '-d'])
