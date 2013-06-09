from __future__ import absolute_import
import logging
import paramiko
from saltcloud import config

log = logging.getLogger(__name__)


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


def client(hostname, identity=None, username=None, password=None, port=22):
    t = paramiko.Transport((hostname, port))

    if identity:
        pkey = paramiko.RSAKey.from_private_key_file(identity)
        t.connect(username=username, pkey=pkey)
    elif password:
        t.connect(username=username, password=password)

    return paramiko.SFTPClient.from_transport(t)


def put(client, local_path, remote_path):
    client.put(
        localpath=local_path,
        remotepath=remote_path)

