from __future__ import absolute_import
import os
# from saltcloud.utils import gen_keys
from cloudseed.utils import ssh
from cloudseed.utils import env
from .writers import write_string
from .filesystem import mkdirs
# from .filesystem import read_file


def master_salt_call_highstate():
    # cloud = env.cloud()
    # client = ssh.master_client(cloud)
    # #ssh.sudo(client, 'salt-call state.highstate')
    # # we want the events, salt-call does not trigger the master events
    # ssh.sudo(client, 'salt \'master\' state.highstate')
    highstate('master')


def highstate(minion_id=None, grain=None):

    cloud = env.cloud()
    client = ssh.master_client(cloud)

    if minion_id:
        ssh.sudo(client, 'salt \'%s\' state.highstate' % minion_id)
    elif grain:
        ssh.sudo(client, 'salt -G \'%s\' state.highstate' % grain)


# def create_default_vagrant_folders(prefix=''):
#     mkdirs(
#         # default vagrant overrides
#         os.path.join(prefix, 'vagrant'),
#         )

def create_default_salt_folders(prefix=''):
    '''
    Create default salt stack folders.

    Match the saltstack default deploy structure
    and the start of the cloudseed environments
    '''
    mkdirs(
        # default sls home
        os.path.join(prefix, 'srv/salt'),

        # custom module home:
        os.path.join(prefix, 'srv/salt/_states'),

        # default pillar home
        os.path.join(prefix, 'srv/pillar'),

        # default salt home
        os.path.join(prefix, 'salt'),
        )


# def create_default_vagrant_files(prefix=''):
#     '''
#     Create the default salt configuration files.
#     '''

#     path_prefix = os.path.join(prefix, 'vagrant')
#     create_vagrant_minion_config(path_prefix)
#     create_vagrant_minion_keys(path_prefix)
#     create_vagrant_vagrantfile()
#     create_vagrant_bootstrap(path_prefix)


def create_default_salt_files(prefix='', data=None):
    '''
    Create the default salt configuration files.
    data param is currently unused.
    '''
    data = {} if data is None else data

    path_prefix = os.path.join(prefix, 'salt')
    create_salt_master_config(path_prefix, data.get('master', None))
    create_salt_cloud_config(path_prefix, data.get('config', None))
    create_salt_cloud_profiles(path_prefix, data.get('profiles', None))
    create_salt_cloud_providers(path_prefix, data.get('providers', None))


# def create_vagrant_vagrantfile(prefix=''):
#     current_path = os.path.join(os.path.dirname(__file__), '../')
#     current_path = os.path.normpath(current_path)

#     cloudseed_deploy_path = os.path.join(current_path, 'deploy')
#     vagrantfile = read_file(os.path.join(cloudseed_deploy_path, 'Vagrantfile'))

#     filename = os.path.join(prefix, 'Vagrantfile')
#     write_string(filename, vagrantfile)


# def create_vagrant_bootstrap(prefix=''):
#     current_path = os.path.join(os.path.dirname(__file__), '../')
#     current_path = os.path.normpath(current_path)

#     cloudseed_deploy_path = os.path.join(current_path, 'deploy')
#     bootstrap = read_file(os.path.join(cloudseed_deploy_path, 'bootstrap-salt.sh'))

#     filename = os.path.join(prefix, 'bootstrap-salt.sh')
#     write_string(filename, bootstrap)


# def create_vagrant_minion_keys(prefix):
#     pem, pub = gen_keys()
#     filename_pem = os.path.join(prefix, 'minion.pem')
#     filename_pub = os.path.join(prefix, 'minion.pub')

#     write_string(filename_pem, pem)
#     write_string(filename_pub, pub)


# def create_vagrant_minion_config(prefix='', data=None):
#     data = '''id: seed-minion.pub
# master: localhost
# grains:
#   roles:
#     - <role>

# '''
#     filename = os.path.join(prefix, 'minion')
#     write_string(filename, data)


def create_salt_cloud_profiles(prefix='', data=None):
    '''
    Salt master config
    The YAML write, though correct, was not pretty
    so we opt for a pretty formatted string
    '''
    data = '''master:
  provider: aws
  image: ami-8e109ebe
  size: Micro Instance
  script: Ubuntu-master
  ssh_username: ubuntu
'''
    filename = os.path.join(prefix, 'cloud.profiles')
    write_string(filename, data)


def create_salt_cloud_providers(prefix='', data=None):
    '''
    Salt master config
    The YAML write, though correct, was not pretty
    so we opt for a pretty formatted string
    '''

    data = '''aws:
  id: <id>
  key: <secret>
  keyname: test_prod_ec2
  private_key: /Users/aventurella/.cloudseed/test/keys/test_prod_ec2
  location: us-west-2
  provider: aws
'''
    filename = os.path.join(prefix, 'cloud.providers')
    write_string(filename, data)


def create_salt_cloud_config(prefix='', data=None):
    '''
    Salt master config
    The YAML write, though correct, was not pretty
    so we opt for a pretty formatted string
    '''
    data = '''start_action: state.highstate
sync_after_install: all
display_ssh_output: False
'''
    filename = os.path.join(prefix, 'cloud')
    write_string(filename, data)


def create_salt_master_config(prefix='', data=None):
    '''
    Salt master config
    The YAML write, though correct, was not pretty
    so we opt for a pretty formatted string
    '''
    data = '''fileserver_backend:
  - roots
  - git

gitfs_remotes:
  - git://github.com/cloudseed-project/cloudseed-states.git

file_roots:
  base:
  - /srv/salt

pillar_roots:
  base:
  - /srv/pillar
'''

    filename = os.path.join(prefix, 'master')
    write_string(filename, data)
