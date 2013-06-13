import sys
import os
import logging
# this will fail on windows
import pwd
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


def _set_user(user):
    log = logging.getLogger('cloudseed')

    try:
        pwuser = pwd.getpwnam(user)
        try:
            os.setgid(pwuser.pw_gid)
            os.setuid(pwuser.pw_uid)
        except OSError:
            log.critical('Unable to change to user \'%s\'', user)
            raise RuntimeError
    except KeyError:
        log.critical('User not found \'%s\'', user)
        raise RuntimeError


def _start_agent(daemon=True):
    log = logging.getLogger('cloudseed')
    sc_log = logging.getLogger('saltcloud')

    log.setLevel(logging.DEBUG)
    sc_log.setLevel(logging.DEBUG)

    if daemon:
        daemonize()
        _set_user('root')
        log_target = logging.FileHandler('/tmp/cloudseed_agent.log')
    else:
        log_target = logging.StreamHandler(sys.stdout)

    log.addHandler(log_target)
    sc_log.addHandler(log_target)
    agent()


def _start_worker(daemon=True):
    log = logging.getLogger('cloudseed')
    sc_log = logging.getLogger('saltcloud')

    log.setLevel(logging.DEBUG)
    sc_log.setLevel(logging.DEBUG)

    if daemon:
        daemonize()
        _set_user('root')
        log_target = logging.FileHandler('/tmp/cloudseed_agent.log')
    else:
        log_target = logging.StreamHandler(sys.stdout)

    log.addHandler(log_target)
    sc_log.addHandler(log_target)
    worker()


def _start_events(daemon=True):
    log = logging.getLogger('cloudseed')
    sc_log = logging.getLogger('saltcloud')

    log.setLevel(logging.DEBUG)
    sc_log.setLevel(logging.DEBUG)

    if daemon:
        daemonize()
        _set_user('root')
        log_target = logging.FileHandler('/tmp/cloudseed_agent.log')
    else:
        log_target = logging.StreamHandler(sys.stdout)

    log.addHandler(log_target)
    sc_log.addHandler(log_target)
    salt_master_events()
