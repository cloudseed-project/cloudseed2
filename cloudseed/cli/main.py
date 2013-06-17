from __future__ import unicode_literals
from __future__ import absolute_import
import os
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
    init <environment>    initialize a new .cloudseed <environment> for the current project
    bootstrap
    ssh                       ssh into the master server, requires bootstrap
    status                    current cloudseed status
    deploy <profile>          deploy a state to a machine
    deploy destroy            destroy a deployed set of virtual machines. This cannot be undone
    sync                      sync states and modules to the currently bootstrapped environment
    '''
    args = docopt(
        cloudseed_main.__doc__,
        version=cloudseed.__version__,
        options_first=True)

    command = args['<command>']
    argv = [args['<command>']] + args['<args>']

    initialize_logging(verbose=False)


    if command == 'push':
        from cloudseed.cli import push
        push.run(argv)
        return

    if command == 'init':
        from cloudseed.cli import initialize
        initialize.run(argv)

    elif command == 'bootstrap':
        from cloudseed.cli import bootstrap
        bootstrap.run(argv)

    elif command == 'ssh':
        from cloudseed.cli import ssh
        ssh.run(argv)

    elif command == 'sync':
        from cloudseed.cli import sync
        sync.run(argv)

    elif command == 'deploy':
        from cloudseed.cli import deploy
        deploy.run(argv)

    elif command == 'status':
        from cloudseed.cli import status
        status.run(argv)

    elif command == 'agent':
        from cloudseed.cli import agent
        agent.run(argv)

    elif command == 'destroy':
        from cloudseed.cli import destroy
        destroy.run(argv)

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

