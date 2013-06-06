import logging
import paramiko
from saltcloud import config
from subprocess import call
import zmq
from zmq.ssh.tunnel import tunnel_connection


log = logging.getLogger(__name__)


def run(client, command):
    # to get the exit code of the command:
    # chan = client.get_transport().open_session()
    # chan.exec_command(command)
    # print('exit status: %s' % chan.recv_exit_status())

    action = 'sh -c "%s"' % command
    stdin, stdout, stderr = client.exec_command(action)
    return stdout.read()


def agent_zmq_tunnel(cloud):
    vm_ = cloud.vm_profile('master')
    server = cloud.opts['cloudseed']['ip_address']
    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    private_key = config.get_config_value('private_key', vm_, cloud.opts)
    username = config.get_config_value('ssh_username', vm_, cloud.opts)

    if private_key:
        tunnel_connection(
                socket,
                'tcp://127.0.0.1:5556',
                '%s@%s' % (username, server),
                keyfile=private_key,
                timeout=60)
    else:
        password = config.get_config_value('password', vm_, cloud.opts)
        tunnel_connection(
                socket,
                'tcp://127.0.0.1:5556',
                '%s@%s' % (username, server),
                password=password,
                timeout=60)

    return socket


def sudo(client, command):
    action = 'sudo sh -c "%s"' % command

    stdin, stdout, stderr = client.exec_command(action)
    return stdout.read()


def master_client(cloud):
    vm_ = cloud.vm_profile('master')
    provider = cloud.provider_profile_full(vm_)

    username = config.get_config_value('ssh_username', vm_, cloud.opts)
    hostname = cloud.opts['cloudseed'].get('ip_address', None)

    if 'private_key' in provider or 'private_key' in vm_:
        private_key = config.get_config_value('private_key', vm_, cloud.opts)

        return client(
            hostname=hostname,
            identity=private_key,
            username=username
            )

    # TODO Locate example of saltcloud using an ssh password
    # so we can use the proper key.


def connect(host, username, identity=None):

    call('ssh {0}@{1} -i {2} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=yes' \
        .format(
            username,
            host,
            identity), shell=True)



def client(hostname, identity=None, username=None, password=None, port=22):

    if identity:
        return _client_with_identity(hostname, port, username, identity)
    elif username and password:
        return _client_with_password(hostname, port, username, password)


def _client_with_identity(hostname, port, username, identity):
    log.debug(
        'Initializing SSH Client: ssh -p %s-i %s %s@%s',
        port, identity, username, hostname)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=hostname,
        port=port,
        username=username,
        key_filename=identity,
        timeout=5)
    return client


def _client_with_password(hostname, port, username, password):
    log.debug(
        'Initializing SSH Client\nhostname: %s\nport: %s\nusername: %s\npassword: %s\n',
        hostname, port, username, password)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        timeout=5)

    return client
