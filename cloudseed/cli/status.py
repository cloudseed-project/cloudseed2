'''
usage:
  cloudseed status

options:
  -h, --help            Show this screen.

'''
from salt.output import display_output
from cloudseed.utils import env
import cloudseed.agent.commands


def run(argv):
    data = cloudseed.agent.commands.status()

    cloud = env.cloud()
    cloud.opts['color'] = True

    display_output(data, out='nested', opts=cloud.opts)
