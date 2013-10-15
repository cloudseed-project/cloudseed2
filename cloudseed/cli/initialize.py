'''
usage:
  cloudseed init [options]

options:
  -n <name>, --name=<name>  Name of the environment to initialize [default: default]
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


log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)
    init(env=args['--name'])
    print('Cloudseed initialized')


def init(env=None):
    create_default_cloudseed_folders()

    if env:
        if env == 'current':
            print('Invalid name, \'current\' is reserved.')
            return

        cwd = os.getcwd()
        prefix = os.path.join(cwd, 'cloudseed', env)
        create_default_salt_folders(prefix)
        create_default_salt_files(prefix)
        create_default_vagrant_folders(prefix)
        create_default_vagrant_files(prefix)

        symlink(prefix, os.path.join(cwd, 'cloudseed', 'current'))
