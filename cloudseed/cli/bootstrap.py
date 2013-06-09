'''
usage:
  cloudseed bootstrap <environment>

options:
  <environment>         The profile name in your cloudseed/ folder to load
  -h, --help            Show this screen.

'''
import os
import tempfile
import saltcloud.cli
import saltcloud.config
import saltcloud.cloud
import cloudseed
from cloudseed.utils import filesystem
from cloudseed.utils import env
from cloudseed.utils import saltcloud as cs_saltcloud
import cloudseed.cloud


# saltcloud_parse_args = saltcloud.cli.SaltCloud.parse_args
# saltcloud_create = saltcloud.cloud.Cloud.create
#cloud = None


def run(argv):
    cs_saltcloud.bootstrap_master()
    # return

    # saltcloud.cli.SaltCloud.parse_args = cloudseed_parse_args
    # # saltcloud.cloud.Cloud.create = cloudseed_create
    # cloud = saltcloud.cli.SaltCloud()
    # cloud.run()




def cloudseed_create(self, vm_):

    data = boostrap_master(self.opts)

    master = filesystem.read_file(self.opts['master_config'])
    profiles = filesystem.read_file(self.opts['vm_config'])
    config = filesystem.read_file(self.opts['conf_file'])
    providers = filesystem.read_file(self.opts['providers_config'])

    vm_['cloudseed'] = data
    vm_['saltcloud'] = {
    'config': config,
    'profiles': profiles,
    'providers': providers}

    vm_['cloudseed'] = {'master': master}

    data = saltcloud_create(self, vm_)
    #ipAddress
    #dnsName

    import pdb; pdb.set_trace()
    foo = 1

    return data


def boostrap_master(config):

    cloud = cloudseed.cloud.Cloud(config)
    provider = cloud.profile_provider('master')

    try:
        cloud.clouds['%s.bootstrap_master' % provider](cloud)
    except KeyError:
        raise


def cloudseed_parse_args(self, args=None, values=None):
    prefix = env.current_env_path()

    cloudseed_args = [
    '--cloud-config', os.path.join(prefix, 'salt', 'cloud'),
    '--profiles', os.path.join(prefix, 'salt', 'cloud.profiles'),
    '--providers-config',  os.path.join(prefix, 'salt', 'cloud.providers'),
    '--master-config',  os.path.join(prefix, 'salt', 'master'),
    '-p', 'master',

    # minion id and Name on ec2
    # we override the minion id below though
    'cloudseed-sample-foo-master'
    ]

    saltcloud_parse_args(self, cloudseed_args, values)
    self.config['minion'] = {'master': 'localhost', 'id': 'master'}

    # if we don't disable the start action,
    # it will wait on the machine bootstrapping
    # the master for a response, instead of on
    # the cloud VM we are creating.
    # for now the highstate on master is handeled
    # in the deploy script
    self.config['start_action'] = None
    self.config['display_ssh_output'] = True

    # override the initial lookup path for modules.
    # ensure that our local clouds are searched first, if present
    # This works with salt.loader.Loaader
    self.config['extension_modules'] = os.path.join(
        os.path.dirname(cloudseed.__file__))

    # load ours
    cloud = cloudseed.cloud.Cloud(self.config)

    vm_profile = cloud.vm_profile('master')
    vm_profile['securitygroup'] = ['default', 'ssh']


    self.config['log_file'] = '/dev/null'

    tempdir = tempfile.mkdtemp()
    filesystem.mkdirs(os.path.join(tempdir, 'minion'))
    self.config['pki_dir'] = tempdir

    # this gets us close, but I don't think it's exactly ideal for
    # the specifi need we have. Revisit later to confirm.
    #self.config['make_master'] = True

    deploy_scripts_search_path = self.config['deploy_scripts_search_path']
    current_path = os.path.join(os.path.dirname(__file__), '../')
    current_path = os.path.normpath(current_path)

    cloudseed_deploy_path = os.path.join(current_path, 'deploy')
    self.config['deploy_scripts_search_path'] = (cloudseed_deploy_path, ) + deploy_scripts_search_path
