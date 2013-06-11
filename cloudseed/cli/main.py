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
  cloudseed [--version] [--verbose] [--help] [-c|--config=<config>]
            [-p|--profile=<profile>] [-r|--provider=<provider>]
            <command> [<args>...]

options:
  -c --config=<config>     config to use
  -p --profile=<profile>   profile to use
  -r --provider=<provider> provider to use
  -h --help                show this screen
  --verbose                show debug output
  --version                show version


common commands:
    init <project>            initialize a new .cloudseed <project>
    init env <environment>    initialize a new .cloudseed <environment> for the current project
    bootstrap <environment>   deploy a salt master for the specified <environment>
    ssh                       ssh into the master server, requires bootstrap
    status                    current cloudseed status
    env <environment>         charge cloudseed environment to specified <environment>
    destroy <environment>     destroys all boxes associated with this environment
    deploy <state>            deploy a state to a machine
    sync                      sync states and modules to the currently bootstrapped environment
    '''
    args = docopt(
        cloudseed_main.__doc__,
        version=cloudseed.__version__)
        #options_first=True)

    command = args['<command>']
    argv = [args['<command>']] + args['<args>']

    initialize_logging(verbose=args['--verbose'])

    # try:
    #     profile_config = os.path.abspath(args['--profile'][0])
    # except IndexError:
    #     profile_config = None

    # try:
    #     local_config = os.path.abspath(args['--config'][0])
    # except IndexError:
    #     local_config = None

    # try:
    #     provider_config = os.path.abspath(args['--provider'][0])
    # except IndexError:
    #     provider_config = None

    # config = Config(FilesystemConfig(
    #     local_config=local_config,
    #     profile_config=profile_config,
    #     provider_config=provider_config))

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

    # elif command == 'agent':
    #     from cloudseed.cli import agent
    #     agent.run(config, argv)


    # elif command == 'instance':
    #     from cloudseed.cli import instance
    #     instance.run(config, argv)

    # elif command == 'status':
    #     from cloudseed.cli import status
    #     status.run(config, argv)

    # elif command == 'env':
    #     from cloudseed.cli import env
    #     env.run(config, argv)

    # elif command == 'destroy':
    #     from cloudseed.cli import destroy
    #     destroy.run(config, argv)

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

