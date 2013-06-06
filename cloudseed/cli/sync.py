'''
usage:
  cloudseed sync

options:
  -h, --help         Show this screen.

'''
import logging
from docopt import docopt
from cloudseed.utils import sync


log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)
    sync.sync_partial()
