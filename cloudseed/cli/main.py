from __future__ import absolute_import
import logging
from subprocess import call
from docopt import docopt
from docopt import DocoptExit
import cloudseed


def cloudseed_main():
    '''
usage:
  cloudseed [--version] [--help]
            <command> [<args>...]

options:
  -h --help                show this screen
  --version                show version


common commands:
    init [options]    initialize a new cloudseed environment
    '''
    args = docopt(
        cloudseed_main.__doc__,
        version=cloudseed.__version__,
        options_first=True)

    command = args['<command>']
    argv = [args['<command>']] + args['<args>']

    initialize_logging(verbose=False)

    if command == 'init':
        from cloudseed.cli import initialize
        initialize.run(argv)

    # elif command == 'env':
    #     from cloudseed.cli import env
    #     env.run(config, argv)

    elif args['<command>'] in ('help', None):
        exit(call(['cloudseed', '--help']))

    else:
        exit('{0} is not a cloudseed command. See \'cloudseed --help\'.' \
            .format(args['<command>']))


def initialize_logging(verbose=False):
    log_level = logging.DEBUG if verbose else logging.INFO

    logger = logging.getLogger('cloudseed')
    logger.setLevel(log_level)

    console = logging.StreamHandler()
    console.setLevel(log_level)

    formatter = logging.Formatter('[%(levelname)s] : %(name)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)


def main():

    try:
        cloudseed_main()
    except DocoptExit:
        exit(call(['cloudseed', '--help']))
    except KeyboardInterrupt:
        pass

