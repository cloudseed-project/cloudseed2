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
from cloudseed.utils.filesystem import symlink
from cloudseed.utils.filesystem import create_default_cloudseed_folders
from cloudseed.utils.salt import create_default_salt_folders
from cloudseed.utils.salt import create_default_salt_files
from cloudseed.utils.vagrant import create_default_vagrant_folders
from cloudseed.utils.vagrant import create_default_vagrant_files
from cloudseed import forms

log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)
    init(name=args['--name'],
         os_id=args['--os'],
         box_id=args['--box'],
         ports=args['--port'],
         bridged=args['--bridge'])

    print('Cloudseed initialized')


def init(name=None, os_id=None, box_id=None, ports=None, bridged=False):

    results = forms.init.run(
        name=name,
        box_id=box_id,
        os_id=os_id,
        ports=ports)

    create_default_cloudseed_folders()

    if name == 'current':
        print('Invalid name, \'current\' is reserved.')
        return

    cwd = os.getcwd()
    prefix = os.path.join(cwd, 'cloudseed', name)
    create_default_salt_folders(prefix)
    create_default_salt_files(prefix)
    create_default_vagrant_folders(prefix)

    create_default_vagrant_files(prefix,
        box=results['box_id'],
        box_url=results['box_url'],
        ports=results['ports'],
        bridged=bridged)

    symlink(prefix, os.path.join(cwd, 'cloudseed', 'current'))
