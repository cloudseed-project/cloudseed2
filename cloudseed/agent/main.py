from .utils import daemonize
from .agent import worker
from .agent import agent
from .agent import salt_master_events


def cloudseed_agent(daemon=True):
    _start_agent(daemon)


def cloudseed_worker(daemon=True):
    _start_worker(daemon)


def cloudseed_events(daemon=True):
    _start_events(daemon)


def _start_agent(daemon=True):
    if daemon:
        daemonize()
    agent()


def _start_worker(daemon=True):
    if daemon:
        daemonize()
    worker()


def _start_events(daemon=True):
    if daemon:
        daemonize()
    salt_master_events()
