from __future__ import absolute_import
import os
import subprocess
from .keys import gen_keys
from .writers import write_string
from .filesystem import mkdirs
from .filesystem import read_file


def create_default_vagrant_folders(prefix=''):
    mkdirs(
        # default vagrant overrides
        os.path.join(prefix, 'vagrant'),
        )


def create_default_vagrant_files(prefix=''):
    '''
    Create the default salt configuration files.
    '''

    path_prefix = os.path.join(prefix, 'vagrant')
    create_vagrant_minion_config(path_prefix)
    create_vagrant_minion_keys(path_prefix)
    create_vagrant_vagrantfile()
    create_vagrant_bootstrap(path_prefix)


def create_vagrant_vagrantfile(prefix=''):
    # TODO handle error if vagrant is not installed.
    p = subprocess.Popen('vagrant init', shell=True)
    p.wait()

    current_path = os.path.join(os.path.dirname(__file__), '../')
    current_path = os.path.normpath(current_path)

    cloudseed_deploy_path = os.path.join(current_path, 'deploy')
    vagrantfile = read_file(os.path.join(cloudseed_deploy_path, 'Vagrantfile'))

    filename = os.path.join(prefix, 'Vagrantfile')
    write_string(filename, vagrantfile)


def create_vagrant_bootstrap(prefix=''):
    current_path = os.path.join(os.path.dirname(__file__), '../')
    current_path = os.path.normpath(current_path)

    cloudseed_deploy_path = os.path.join(current_path, 'deploy')

    bootstrap = read_file(
        os.path.join(cloudseed_deploy_path, 'bootstrap-salt.sh'))

    filename = os.path.join(prefix, 'bootstrap-salt.sh')
    write_string(filename, bootstrap)


def create_vagrant_minion_keys(prefix):
    pem, pub = gen_keys()
    filename_pem = os.path.join(prefix, 'minion.pem')
    filename_pub = os.path.join(prefix, 'minion.pub')

    write_string(filename_pem, pem)
    write_string(filename_pub, pub)


def create_vagrant_minion_config(prefix='', data=None):
    data = '''id: seed-minion.pub
master: localhost
grains:
  roles:
    - <role>

'''
    filename = os.path.join(prefix, 'minion')
    write_string(filename, data)
