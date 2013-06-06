import os
import sys
import logging
from cloudseed.utils import env
from cloudseed.utils import ssh

log = logging.getLogger(__name__)


def master_tunnel(fun):
    def action(*args, **kwargs):
        cloud = env.cloud()
        socket = ssh.agent_zmq_tunnel(cloud)
        socket.send_json(fun(*args, **kwargs))
    return action


# http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
def daemonize():
    '''
    do the UNIX double-fork magic, see Stevens' "Advanced
    Programming in the UNIX Environment" for details (ISBN 0201563177)
    http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
    '''
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError, e:
        log.error('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)

    # decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError, e:
        log.error('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)


    # A normal daemonization redirects the process output to /dev/null.
    # Unfortunately when a python multiprocess is called the output is
    # not cleanly redirected and the parent process dies when the
    # multiprocessing process attempts to access stdout or err.
    #dev_null = open(os.devnull, 'rw')
    #os.dup2(dev_null.fileno(), sys.stdin.fileno())
    #os.dup2(dev_null.fileno(), sys.stdout.fileno())
    #os.dup2(dev_null.fileno(), sys.stderr.fileno())
