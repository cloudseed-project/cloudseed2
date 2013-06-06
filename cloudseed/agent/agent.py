import os
import logging
import time
from multiprocessing import Process
import subprocess
import zmq


log = logging.getLogger(__name__)


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
                p = Process(target=saltcloud_profile, args=(profile, tag))
                p.daemon = True
                p.start()


def saltcloud_profile(name, tag):
    # TODO get the data back and write the record
    # OR hook into the salt event system
    # So we get notified after the provisioning completes
    # See salt.utils.event.MasterEvent || SaltEvent

    out_stream = subprocess.PIPE
    err_stream = subprocess.PIPE
    args = ['salt-cloud', '-p', 'minion', 'minion0']

    p = subprocess.Popen(
        args,
        shell=True,
        stdout=out_stream,
        stderr=err_stream)

    (stdout, stderr) = p.communicate()

    stdout.strip()
    stderr.strip()

    print(stdout)
    print(p.returncode)
    os._exit(0)

    # if p.returncode not in (0, ):
    #     return
    # subprocess.call(['salt-cloud', '-p', name, tag])

