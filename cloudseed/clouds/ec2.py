import logging
import yaml
from saltcloud.clouds.ec2 import *
import saltcloud.config as config
import cloudseed.cloud
from cloudseed.compat import urlquote
from cloudseed.utils import filesystem
from cloudseed.utils import writers
from cloudseed.utils import env
from cloudseed.utils import sync
from cloudseed.utils import salt
from cloudseed.utils import events
import cloudseed.agent.commands


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

    return create_minion(vm_, call)


def create_minion(vm_, call=None):
    # always assumes the master has been created
    # and that we are running on it.
    bootstrap_minion(vm_)
    data = saltcloud_ec2_create(vm_)

    conf = {
    'ip_address': data['ipAddress'],
    'dns_name': data['dnsName'],
    'private_ip_address': data['privateIpAddress'],
    'instance_id': data['instanceId'],
    'profile': vm_.get('profile', None),
    'name': vm_['name']
    }

    event = {
    'fun': 'create.minion',
    'return': conf
    }

    # assumes being run on the master
    log.debug('Notifying cloudseed \'%s\' is ready %s', vm_['name'], conf)
    events.fire_event(event)
    return data


def create_master(vm_=None, call=None):
    # always assumes we are running locally, creating a
    # master for the 1st time
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
    'private_ip_address': data['privateIpAddress'],
    'instance_id': data['instanceId'],
    'profile': vm_.get('profile', None),
    'name': vm_['name'],
    }

    conf_filename = os.path.join(env.current_env_path(), 'salt', 'cloudseed')

    with open(conf_filename, 'w') as f:
        f.write(yaml.safe_dump(conf, default_flow_style=False))

    sync.sync_full()
    salt.master_salt_call_highstate()

    event = {
    'fun': 'create.master',
    'return': conf
    }

    # assumes being run locally
    cloudseed.agent.commands.fire_event(event)

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


def bootstrap_minion(vm_):
    log.debug('Bootstrapping Minion %s', vm_)

    cloud = cloudseed.cloud.Cloud(__opts__)
    provider = cloud.provider_profile_full(vm_)
    securitygroups = provider.get('securitygroup', [])

    create_securitygroup(
            name=vm_['name'],
            description='CloudseedApp')

    # merge security groups
    vm_['securitygroup'] = securitygroups + [vm_['name']]


def bootstrap_master(cloud):
    vm_ = cloud.vm_profile('master')
    provider = cloud.provider_profile_full(vm_)

    provider['ssh_interface'] = 'public_ips'
    append_data = {}

    if not provider.get('keyname', False):
        keyname = '%s-%s' % (env.location_name(), env.env_name())

        filename = os.path.join(
            env.current_env_path(),
            'salt',
            '%s.pem' % keyname)

        bootstrap_create_keypair(keyname, filename)

        # set it for the current command
        provider['keyname'] = keyname
        provider['private_key'] = filename

        append_data['keyname'] = keyname
        append_data['private_key'] = 'cloudseed/current/salt/%s.pem' % keyname

    else:
        if not os.path.isabs(provider['private_key']):
            new_path = os.path.abspath(provider['private_key'])
            provider['private_key'] = new_path

    # perhaps run though saltcloud's config look up system?
    # see if the security group is defined on the profile
    # or just assume with cloudseed we are looking for the
    # provider only at this stage.
    app, ssh = initial_security_groups()

    if not provider.get('securitygroup', False):
        app_id = create_securitygroup(
            name=app,
            description='CloudseedApp')

        ssh_id = create_securitygroup(
            name=ssh,
            description='CloudseedAppSSH')

        if app_id:
            authorize_ssh_public(ssh_id)

        if ssh_id:
            authorize_all_intragroup(app_id)

        # master gets both groups, minions
        # will only receive the app group
        # unless their profiles specify otherwise
        vm_['securitygroup'] = [app, ssh]
        append_data['securitygroup'] = [app]
    else:
        if ssh not in provider['securitygroup']:
            provider['securitygroup'].append(ssh)

    # write down and new data
    if append_data:
        provider_bytes = filesystem.read_file(cloud.opts['providers_config'])
        provider_data = yaml.load(provider_bytes)
        provider_name = vm_['provider']

        target = provider_data[provider_name]
        target.update(append_data)
        writers.write_yaml(cloud.opts['providers_config'], provider_data)


def initial_security_groups():
    app_group = security_group_name()
    ssh_group = security_group_name('ssh')

    return app_group, ssh_group


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


def create_securitygroup(name, description):

    params = {'Action': 'CreateSecurityGroup'}
    params['GroupName'] = name

    # AWS doesn't like the + encoded space or something.
    # need to figure that out later what's going on there.
    params['GroupDescription'] = description

    location = get_location()
    result = query(params, location=location, return_root=True)

    if 'error' in result:
        code = result['error']['Errors']['Error']['Code']
        if code != 'InvalidGroup.Duplicate':
            log.error(result)
            return None
    else:

        group_id = next(v for each in result
                        for k, v in each.iteritems()
                        if k == 'groupId')

        return group_id


def authorize_all_intragroup(group_id):
    authorize_icmp_intragroup(group_id)
    authorize_udp_intragroup(group_id)
    authorize_tcp_intragroup(group_id)


def authorize_ssh_public(group_id):
    authorize_securitygroup(
        group_id,
        cidr_ip='0.0.0.0/0',
        ip_protocol='tcp',
        from_port=22,
        to_port=22)


def authorize_icmp_intragroup(group_id):
    authorize_securitygroup(
        group_id,
        src_group=group_id,
        ip_protocol='icmp',
        from_port=-1,
        to_port=-1)


def authorize_udp_intragroup(group_id):
    authorize_securitygroup(
        group_id,
        src_group=group_id,
        ip_protocol='udp',
        from_port=1,
        to_port=65535)


def authorize_tcp_intragroup(group_id):
    authorize_securitygroup(
        group_id,
        src_group=group_id,
        ip_protocol='tcp',
        from_port=1,
        to_port=65535)


def authorize_securitygroup(group_id, ip_protocol, from_port, to_port,
                            src_group=None, cidr_ip=None):

    params = {'Action': 'AuthorizeSecurityGroupIngress'}
    params['GroupId'] = group_id
    params['IpPermissions.1.IpProtocol'] = ip_protocol
    params['IpPermissions.1.FromPort'] = from_port
    params['IpPermissions.1.ToPort'] = to_port

    if src_group:
        params['IpPermissions.1.Groups.1.GroupId'] = src_group
    elif cidr_ip:
        params['IpPermissions.1.IpRanges.1.CidrIp'] = cidr_ip

    location = get_location()
    result = query(params, location=location, return_root=True)

    if 'error' in result:
        code = result['error']['Errors']['Error']['Code']
        if code != 'InvalidGroup.Duplicate':
            log.error(result)
            return None
