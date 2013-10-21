from __future__ import absolute_import
import os
import subprocess
import jinja2
from .writers import write_string
from .filesystem import mkdirs
from .filesystem import read_file
from .filesystem import resource_path


def create_default_vagrant_folders(prefix=''):
    mkdirs(
        # default vagrant overrides
        os.path.join(prefix, 'vagrant'),
        )


def create_default_vagrant_files(prefix='', **kwargs):
    '''
    Create the default salt configuration files.
    supported kwargs (for creating vagrant file):
    box, box_url, ports
    '''

    path_prefix = os.path.join(prefix, 'vagrant')
    create_vagrant_minion_config(path_prefix)
    create_vagrant_minion_keys(path_prefix)
    create_vagrant_vagrantfile(**kwargs)


def create_vagrant_vagrantfile(prefix='', **kwargs):
    # TODO handle error if vagrant is not installed.
    p = subprocess.Popen('vagrant init', shell=True)
    p.wait()

    cloudseed_deploy_path = resource_path()

    vagrantfile = read_file(os.path.join(cloudseed_deploy_path, 'Vagrantfile'))
    template = jinja2.Template(vagrantfile)
    filename = os.path.join(prefix, 'Vagrantfile')
    write_string(filename, template.render(kwargs))


def create_vagrant_minion_keys(prefix):

    resources = resource_path()
    pem = read_file(os.path.join(resources, 'minion.pem'))
    pub = read_file(os.path.join(resources, 'minion.pub'))

    filename_pem = os.path.join(prefix, 'minion.pem')
    filename_pub = os.path.join(prefix, 'minion.pub')

    write_string(filename_pem, pem)
    write_string(filename_pub, pub)


def create_vagrant_minion_config(prefix='', data=None):
    data = '''id: minion
master: localhost
grains:
  roles:
    - vagrant

'''
    filename = os.path.join(prefix, 'minion')
    write_string(filename, data)
