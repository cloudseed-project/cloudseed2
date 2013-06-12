from __future__ import absolute_import
import logging
from salt.utils.event import SaltEvent

log = logging.getLogger(__name__)


def fire_event(data, tag='cloudseed'):
    event = SaltEvent('master', '/var/run/salt/master')
    log.debug('Sending salt event %s with tag \'%s\'', data, tag)
    event.fire_event(data, tag)
