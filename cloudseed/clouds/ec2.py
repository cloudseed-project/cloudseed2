import logging
import yaml
from saltcloud.clouds.ec2 import *
import saltcloud.config as config
import cloudseed.cloud
from cloudseed.utils import filesystem
from cloudseed.utils import writers
from cloudseed.utils import env
from cloudseed.utils import sync
from cloudseed.utils import salt


log = logging.getLogger(__name__)
saltcloud_ec2_create = saltcloud.clouds.ec2.create


def __virtual__():
    saltcloud.clouds.ec2.__opts__ = __opts__
    saltcloud.clouds.ec2.__grains__ = {}
    saltcloud.clouds.ec2.__pillar__ = {}

    saltcloud.clouds.ec2.get_configured_provider = get_configured_provider

    if get_configured_provider() is False:
        log.debug(
            'There is no EC2 cloud provider configuration available. Not '
            'loading module'
        )
        return False

    return 'ec2'


def sync_full_manifest(manifest):
    cloud = cloudseed.cloud.Cloud(__opts__)
    vm_ = cloud.vm_profile('master')

    keyname = '%s-%s' % (env.location_name(), env.env_name())

    filename = os.path.join(
        env.current_env_path(),
        'salt',
        '%s.pem' % keyname)

    manifest.add(filename, '/etc/salt/cloud.pem')

    # changing the path to the private_key file to work on
    # the bootstrapped master
    providers = filesystem.read_file(__opts__['providers_config'])

    providers_data = yaml.load(providers)
    master_provider = providers_data[vm_['provider']]

    master_provider['private_key'] = '/etc/salt/cloud.pem'
    cloud_providers = yaml.safe_dump(providers_data, default_flow_style=False)

    manifest.remove('cloudseed/current/salt/cloud.providers')

    manifest.add(
        writers.write_stringio(cloud_providers),
        '/etc/salt/cloud.providers')


def sync_partial_manifest(manifest):
    pass


def sync_full_action(run, sudo):
    sudo('chmod 600 /etc/salt/cloud.pem')


def sync_partial_action(run, sudo):
    pass


def create(vm_=None, call=None):
    if vm_['profile'] == 'master':
        return create_master(vm_, call)

    return saltcloud_ec2_create(vm_)


def create_master(vm_=None, call=None):
    cloud = cloudseed.cloud.Cloud(__opts__)
    bootstrap_master(cloud)

    master = filesystem.read_file(__opts__['master_config'])

    vm_['cloudseed'] = {
        'master': master
    }

    data = saltcloud_ec2_create(vm_)

    if 'Errors' in data:
        message = data['Errors']['Error']['Message']
        log.error('%s', message)
        return

    conf = {
    'ip_address': data['ipAddress'],
    'dns_name': data['dnsName'],
    }

    conf_filename = os.path.join(env.current_env_path(), 'salt', 'cloudseed')

    with open(conf_filename, 'w') as f:
        f.write(yaml.safe_dump(conf, default_flow_style=False))

    sync.sync_full()
    salt.highstate(minion_id='master')

    return data


def get_configured_provider():
    '''
    Return the first configured instance.
    '''
    return config.is_provider_configured(
        __opts__,
        'ec2',
        ('id', 'key')
    )


def bootstrap_master(cloud):
    vm_ = cloud.vm_profile('master')
    provider = cloud.provider_profile_full(vm_)

    #
    # [{'private_key': '/Users/aventurella/.cloudseed/test/keys/test_prod_ec2', 'securitygroup': ['default', 'ssh'], 'ssh_interface': 'public_ips', 'keyname': 'test_prod_ec2', 'location': 'us-west-2', 'key': 'ARI12QQjvliP5pQFQCUlpDI348EvquaAzBEw+V9k', 'provider': 'ec2', 'id': 'AKIAIFMCWURC2SJ4I36Q'}]
    #

    provider['ssh_interface'] = 'public_ips'

    #application_group = security_group_name()
    #provider['securitygroup'] = ['ssh', 'default', ' bigMETHOD-Worker']

    if not provider.get('keyname', False):
        keyname = '%s-%s' % (env.location_name(), env.env_name())

        filename = os.path.join(
            env.current_env_path(),
            'salt',
            '%s.pem' % keyname)

        bootstrap_create_keypair(keyname, filename)
        provider['keyname'] = keyname
        provider['private_key'] = filename

        provider_bytes = filesystem.read_file(cloud.opts['providers_config'])
        provider_data = yaml.load(provider_bytes)
        provider_name = vm_['provider']

        target = provider_data[provider_name]
        target['keyname'] = keyname
        target['private_key'] = 'cloudseed/current/salt/%s.pem' % keyname

        writers.write_yaml(cloud.opts['providers_config'], provider_data)
    else:
        if not os.path.isabs(provider['private_key']):
            new_path = os.path.abspath(provider['private_key'])
            provider['private_key'] = new_path


    #securitygroup:
  #  - default
  #  - ssh



def security_group_name(name=None):
    location_name = env.location_name()
    env_name = env.env_name()

    if name:
        return 'cloudseed-%s-%s-%s' % (location_name, env_name, name)

    return 'cloudseed-%s-%s' % (location_name, env_name)


def bootstrap_create_keypair(keyname, filename):

    result = create_keypair({'keyname': keyname}, call='function')

    if 'error' in result:
        raise RuntimeError

    for each in result:
        key, value = each.popitem()
        if key == 'keyName':
            keyname = keyname
        elif key == 'keyMaterial':
            data = value

    writers.write_string(filename, data)
    os.chmod(filename, 0600)


def create_securitygroup(name):
    pass

