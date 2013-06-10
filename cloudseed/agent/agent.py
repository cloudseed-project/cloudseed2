import os
import logging
import time
import json
import threading
import multiprocessing
import subprocess
import zmq
import salt.utils.event
from cloudseed.utils import saltcloud as cs_saltcloud

log = logging.getLogger(__name__)


def salt_master_events():

    event = salt.utils.event.MasterEvent('/var/run/salt/master')
    from pprint import pprint

    log = logging.getLogger('cloudseed_events')
    log_target = logging.FileHandler('/tmp/cloudseed_events.log')
    log.addHandler(log_target)
    log.debug('Starting Cloudseed Reactor')
    for data in event.iter_events():

        pprint(data)

        if not isinstance(data, dict):
            print(data)
            return

        if data.get('success', False) and \
           data.get('cmd', None) == '_return' and \
           data.get('fun', None) == 'state.highstate':

            log.debug('%s', data)


def agent():
    context = zmq.Context()

    external = context.socket(zmq.REP)
    external.bind('tcp://127.0.0.1:5556')

    agent = context.socket(zmq.PUSH)
    agent.bind("tcp://127.0.0.1:5557")

    poller = zmq.Poller()
    poller.register(external, zmq.POLLIN)

    time.sleep(1)

    log.debug('Agent Started')

    while True:
        socks = dict(poller.poll())

        if socks.get(external) == zmq.POLLIN:
            message = external.recv_json()
            log.debug('agent received command')
            agent.send_json(message)
            log.debug('agent sending ack')
            external.send_json({'ok': True})


def worker():
    context = zmq.Context()

    # Set up a channel to receive work from the ventilator
    agent = context.socket(zmq.PULL)
    agent.connect("tcp://127.0.0.1:5557")

    poller = zmq.Poller()
    poller.register(agent, zmq.POLLIN)
    log.debug('Worker Started')

    while True:
        socks = dict(poller.poll())

        if socks.get(agent) == zmq.POLLIN:
            message = agent.recv_json()
            log.debug('Worker received message %s', message)

            action = message.get('action', None)
            if action == 'profile':
                # depending on how many actions come in
                # we may need to build in a way to limit the
                # number of processes we spawn.
                profile = message['profile']
                tag = message['tag']
                log.debug('Bootstrapping profile %s with tag %s', profile, tag)
                cs_saltcloud.execute_profile(profile, tag)
