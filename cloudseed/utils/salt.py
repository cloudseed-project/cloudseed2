from __future__ import absolute_import
import os
from cloudseed.utils import env
from .writers import write_string
from .filesystem import mkdirs


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


def create_default_salt_files(prefix='', data=None):
    '''
    Create the default salt configuration files.
    data param is currently unused.
    '''
    data = {} if data is None else data

    path_prefix = os.path.join(prefix, 'salt')
    create_salt_master_config(path_prefix, data.get('master', None))
    create_salt_cloud_config(path_prefix, data.get('config', None))
    # create_salt_cloud_profiles(path_prefix, data.get('profiles', None))
    # create_salt_cloud_providers(path_prefix, data.get('providers', None))


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
    data = '''
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
  - git://github.com/cloudseed-project/cloudseed-formulas.git

file_roots:
  base:
  - /srv/salt

pillar_roots:
  base:
  - /srv/pillar
'''

    filename = os.path.join(prefix, 'master')
    write_string(filename, data)
