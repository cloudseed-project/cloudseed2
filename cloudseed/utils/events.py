from __future__ import absolute_import
import zmq
from saltcloud import config
from salt.utils.event import SaltEvent
from cloudseed.utils import ssh
from cloudseed.compat import urlparse
from cloudseed.utils import env


def fire_event(data, tag=None):
    event = SaltEvent('master', '/var/run/salt/master')
    event.fire_event(data, tag)
