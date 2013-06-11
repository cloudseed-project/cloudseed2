import logging
import time
import zmq
import salt.utils.event
import cloudseed.agent.actions


def salt_master_events():

    event = salt.utils.event.MasterEvent('/var/run/salt/master')

    log = logging.getLogger('cloudseed_events')
    log_target = logging.FileHandler('/tmp/cloudseed_events.log')
    log.addHandler(log_target)
    log.debug('Starting Cloudseed Reactor')

    for data in event.iter_events(tag='cloudseed'):
        log.debug('%s', data)

        action = data.get('fun', None)

        if action in ('create.master', 'create.minion'):
            index = {
            'create.master': cloudseed.agent.actions.register_master,
            'create.minion': cloudseed.agent.actions.register_minion}
            try:
                index[action](data['return'])
            except Exception as e:
                log.exception(e)


def agent():
    log = logging.getLogger('cloudseed_agent')
    log_target = logging.FileHandler('/tmp/cloudseed_agent.log')
    log.addHandler(log_target)
    log.debug('Starting Cloudseed Agent')

    context = zmq.Context()

    external = context.socket(zmq.REP)
    external.bind('tcp://127.0.0.1:5556')

    agent = context.socket(zmq.PUSH)
    agent.bind("tcp://127.0.0.1:5557")

    poller = zmq.Poller()
    poller.register(external, zmq.POLLIN)

    # let it all get warmed up
    time.sleep(1)

    log.debug('Cloudseed Agent Started')

    while True:
        socks = dict(poller.poll())

        if socks.get(external) == zmq.POLLIN:
            message = external.recv_json()

            action = message.get('action', None)
            log.debug('Cloudseed agent received command %s', action)

            ret = {'ok': True}

            if action == 'profile':
                agent.send_json(message)

            elif action == 'event':
                tag = message.get('tag', 'cloudseed')
                data = message.get('data', {})
                cloudseed.agent.actions.dispatch_event(data, tag)

            elif action == 'status':
                ret['data'] = cloudseed.agent.actions.status()

            log.debug('Cloudseed agent sending ack %s', ret)
            external.send_json(ret)


def worker():

    log = logging.getLogger('cloudseed_worker')
    log_target = logging.FileHandler('/tmp/cloudseed_worker.log')
    log.addHandler(log_target)
    log.debug('Starting Cloudseed Worker')

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
            log.debug('Received action %s', action)
            if action == 'profile':
                profile = message['profile']
                tag = message['tag']

                cloudseed.agent.actions.execute_profile(profile, tag)
