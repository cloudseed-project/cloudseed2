import logging
from saltcloud.cli import SaltCloud
from cloudseed.cloud import Cloud
from cloudseed.utils import saltcloud as cs_saltcloud
from cloudseed.utils import events as cs_events
from .resources import MongoResource
from .services import CloudseedService


log = logging.getLogger(__name__)


def register_minion(data):
    log.debug('Registering minion %s', data)
    # service = CloudseedService(MongoResource())
    # service.add_machine(tag, data)


def register_master(data):
    log.debug('Registering master %s', data)
    service = CloudseedService(MongoResource())
    service.init_cloudseed(data)


def dispatch_event(data, tag):
    log.debug('Dispatching event %s with tag %s', data, tag)
    try:
        cs_events.fire_event(data, tag=tag)
    except Exception as e:
        log.exception(e)


def next_seq():
    service = CloudseedService(MongoResource())
    return service.next_seq()


def status():
    log.debug('Fetching status')
    service = CloudseedService(MongoResource())
    return service.machines()


def execute_profile(profile, tag=None):
    # depending on how many actions come in
    # we may need to build in a way to limit the
    # number of processes we spawn.
    log.debug('Bootstrapping profile %s with tag %s', profile, tag)
    cs_saltcloud.execute_profile(profile, tag)
