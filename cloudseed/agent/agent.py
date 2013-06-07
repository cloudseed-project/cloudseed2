import os
import logging
import time
import json
import threading
import multiprocessing
import subprocess
import zmq
import salt.utils.event

log = logging.getLogger(__name__)


def salt_master_events():

    event = salt.utils.event.MasterEvent('/var/run/salt/master')
    from pprint import pprint

    for data in event.iter_events():
        print(type(data))

        if not isinstance(data, dict):
            print(data)
            return

        pprint(data)

        if data.get('success', False) and \
           data.get('_cmd', None) == '_return' and \
           data.get('fun', None) == 'state.highstate':

            print(data)


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

                action = SaltCloudProfile(profile, tag)
                action.start()


class SaltCloudProfile(multiprocessing.Process):
    def __init__(self, profile, tag):
        self.profile = profile
        self.tag = tag
        #self.stdout = None
        #self.stderr = None
        super(SaltCloudProfile, self).__init__()

    def run(self):
        args = [
        'salt-cloud',
        '-p', self.profile,
        self.tag]

        p = subprocess.Popen(
        args)

        #output, _ = p.communicate()
        #print(output)
        p.wait()
        #retcode = p.poll()


# class SaltCloudProfile(threading.Thread):
#     def __init__(self, profile, tag):
#         self.profile = profile
#         self.tag = tag
#         self.stdout = None
#         self.stderr = None
#         super(SaltCloudProfile, self).__init__()

#     def run(self):
#         out_stream = subprocess.PIPE
#         args = ['salt-cloud', '-p', self.profile, self.tag]

#         p = subprocess.Popen(
#         args,
#         stdout=out_stream)

#         output, _ = p.communicate()
#         #retcode = p.poll()
