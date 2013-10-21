'''
usage:
  cloudseed init [options] [(--os=<os> --box=<box>)][--port=<port>...]

options:
  -n <name>, --name=<name>  Name of the environment to initialize [default: default]
  -o <os>, --os=<os>        OS id to use
  -b <box>, --box=<box>     Box id to use
  -p <port>, --port=<port>  Enable port forwarding for the specified ports.
  -g, --bridge              Enable Bridged Networking
  -h, --help                Show this screen.


'''
import os
import logging
from docopt import docopt
from cloudseed import actions
log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)
    message = 'Cloudseed initialized'

    try:
        init(name=args['--name'],
             os_id=args['--os'],
             box_id=args['--box'],
             ports=args['--port'],
             bridged=args['--bridge'])
    except:
        message = 'Cloudseed failed to initialize'

    print(message)


def init(name='default', os_id=None, box_id=None, ports=None, bridged=False):

    cwd = os.getcwd()
    try:
        actions.init.run(
            path=cwd,
            name=name,
            box_id=box_id,
            os_id=os_id,
            ports=ports,
            bridged=bridged)
    except ValueError as e:
        print(e.message)
        raise
