'''
usage:
  cloudseed bootstrap <environment>

options:
  <environment>         The profile name in your cloudseed/ folder to load
  -h, --help            Show this screen.

'''

from cloudseed.utils import saltcloud


def run(argv):
    saltcloud.bootstrap_master()
