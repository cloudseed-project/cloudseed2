'''
usage:
  cloudseed agent

options:
  -h, --help         Show this screen.
  <profile>          The state you would like to deploy
'''
import logging
from docopt import docopt
from cloudseed.agent import main

log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)
    main.main()


