from multiprocessing import Process
from .utils import daemonize
from .agent import worker
from .agent import agent
from .agent import salt_master_events


def main():
    _start_daemon()


def _start_daemon():
    daemonize()
    Process(name='cloudseed worker', target=worker).start()
    Process(name='cloudseed agent', target=agent).start()
    Process(name='cloudseed salt events', target=salt_master_events).start()


if __name__ == '__main__':
    main()
