from multiprocessing import Process
from .utils import daemonize
from .agent import worker
from .agent import agent
from .agent import salt_master_events


def cloudseed_agent():
    _start_agent()


def cloudseed_worker():
    _start_worker()


def cloudseed_events():
    _start_events()


def _start_agent():
    daemonize()
    agent()


def _start_worker():
    daemonize()
    worker()
    Process(name='cloudseed worker', target=worker).start()


def _start_events():
    daemonize()
    salt_master_events()
