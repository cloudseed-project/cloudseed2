'''
usage:
  cloudseed status

options:
  -h, --help            Show this screen.

'''
from salt.output import display_output
import cloudseed.agent.commands


def run(argv):
    data = cloudseed.agent.commands.status()
    opts = {'color': True}
    display_output(data, out='yaml', opts=opts)
