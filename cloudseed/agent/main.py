import sys
import logging
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
    log = logging.getLogger('cloudseed')
    log.setLevel(logging.DEBUG)
    if daemon:
        daemonize()
        log_target = logging.FileHandler('/tmp/cloudseed_agent.log')
    else:
        log_target = logging.StreamHandler(sys.stdout)

    log.addHandler(log_target)
    agent()


def _start_worker(daemon=True):
    log = logging.getLogger('cloudseed')
    log.setLevel(logging.DEBUG)

    if daemon:
        daemonize()
        log_target = logging.FileHandler('/tmp/cloudseed_agent.log')
    else:
        log_target = logging.StreamHandler(sys.stdout)

    log.addHandler(log_target)
    worker()


def _start_events(daemon=True):
    log = logging.getLogger('cloudseed')
    log.setLevel(logging.DEBUG)

    if daemon:
        daemonize()
        log_target = logging.FileHandler('/tmp/cloudseed_agent.log')
    else:
        log_target = logging.StreamHandler(sys.stdout)

    log.addHandler(log_target)
    salt_master_events()
