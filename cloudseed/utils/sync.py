import os
import tempfile
import functools
from cloudseed.utils import sftp
from cloudseed.utils import ssh
from cloudseed.utils.archive import Manifest
from cloudseed.utils.archive import Archive
from cloudseed.utils import env


def sync_archive(local, remote, cloud):
    sftp_client = sftp.master_client(cloud)
    sftp.put(sftp_client, local, remote)


def sync_partial():
    cloud = env.cloud()

    file_roots = cloud.opts['file_roots']['base'][0]
    pillar_roots = cloud.opts['pillar_roots']['base'][0]

    manifest = Manifest()
    manifest.add('cloudseed/current/srv/salt', file_roots)
    manifest.add('cloudseed/current/srv/pillar', pillar_roots)
    manifest.add('cloudseed/current/salt/cloud.profiles', '/etc/salt/cloud.profiles')

    vm_ = cloud.vm_profile('master')
    provider = cloud.provider(vm_)

    action = cloud.clouds.get('%s.sync_partial_manifest' % provider, lambda x: None)
    action(manifest)

    tmp = tempfile.NamedTemporaryFile(delete=False)
    Archive.tar(tmp, manifest)
    _sync_partial_action(tmp.name, cloud)


def sync_full():

    cloud = env.cloud()

    file_roots = cloud.opts['file_roots']['base'][0]
    pillar_roots = cloud.opts['pillar_roots']['base'][0]

    manifest = Manifest()
    manifest.add('cloudseed/current/srv/salt', file_roots)
    manifest.add('cloudseed/current/srv/pillar', pillar_roots)
    manifest.add('cloudseed/current/salt/cloud.profiles', '/etc/salt/cloud.profiles')
    manifest.add('cloudseed/current/salt/cloud.providers', '/etc/salt/cloud.providers')
    manifest.add('cloudseed/current/salt/cloud', '/etc/salt/cloud')

    vm_ = cloud.vm_profile('master')
    provider = cloud.provider(vm_)

    action = cloud.clouds.get('%s.sync_full_manifest' % provider, lambda x: None)
    action(manifest)

    tmp = tempfile.NamedTemporaryFile(delete=False)
    Archive.tar(tmp, manifest)

    _sync_full_action(tmp.name, cloud)


def _sync_action(filename, cloud, run, sudo):

    run('mkdir -p /tmp/cloudseed')

    base = os.path.basename(filename)
    sync_archive(
        local=filename,
        remote='/tmp/cloudseed/%s' % base,
        cloud=cloud)

    os.unlink(filename)

    sudo('tar -C / -xzf /tmp/cloudseed/%s' % base)
    run('rm -rf /tmp/cloudseed')


def _sync_full_action(filename, cloud):
    ssh_client = ssh.master_client(cloud)
    sudo = functools.partial(ssh.sudo, ssh_client)
    run = functools.partial(ssh.run, ssh_client)

    vm_ = cloud.vm_profile('master')
    provider = cloud.provider(vm_)

    _sync_action(filename, cloud, run, sudo)


    sudo('chmod 600 /etc/salt/cloud.profiles')
    sudo('chmod 600 /etc/salt/cloud.providers')
    sudo('chmod 600 /etc/salt/cloud')

    provider_action = cloud.clouds.get(
        '%s.sync_full_action' % provider,
        lambda x, y: None)

    provider_action(run, sudo)


def _sync_partial_action(filename, cloud):
    ssh_client = ssh.master_client(cloud)
    sudo = functools.partial(ssh.sudo, ssh_client)
    run = functools.partial(ssh.run, ssh_client)

    vm_ = cloud.vm_profile('master')
    provider = cloud.provider(vm_)

    _sync_action(filename, cloud, run, sudo)

    sudo('chmod 600 /etc/salt/cloud.profiles')

    provider_action = cloud.clouds.get(
        '%s.sync_full_action' % provider,
        lambda x, y: None)

    provider_action(run, sudo)
