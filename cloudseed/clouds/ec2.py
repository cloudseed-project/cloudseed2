import logging
import yaml
from saltcloud.clouds.ec2 import *
import saltcloud.config as config
import cloudseed.cloud
from cloudseed.compat import urlquote
from cloudseed.compat import string_type
from cloudseed.utils import filesystem
from cloudseed.utils import writers
from cloudseed.utils import env
from cloudseed.utils import sync
from cloudseed.utils import salt
from cloudseed.utils import events
import cloudseed.agent.commands


# IMPORTANT: there is some patching performed at the bottom of this file.
log = logging.getLogger(__name__)


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

    log.debug('VM: %s', vm_)
    log.debug('VM Created: %s', data)

    conf = {
    'ip_address': data['ipAddress'],
    'dns_name': data['dnsName'],
    'private_ip_address': data['privateIpAddress'],
    'instance_id': data['instanceId'],
    'profile': vm_.get('profile', None),
    'name': vm_['name'],
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
    log.debug('VM: %s', vm_)
    log.debug('VM Created: %s', data)

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

    securitygroups = config.get_config_value(
        'securitygroup',
         vm_,
         __opts__)

    marker = marker_security_group()

    create_securitygroup(
            name=vm_['name'],
            description='CloudseedApp')

    # merge security groups
    vm_['securitygroup'] = securitygroups + [vm_['name'], marker]


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

    groups = bootstrap_master_security_groups(vm_, provider)
    append_data['securitygroup'] = groups

    # write down and new data
    if append_data:
        provider_bytes = filesystem.read_file(cloud.opts['providers_config'])
        provider_data = yaml.load(provider_bytes)
        provider_name = vm_['provider']

        target = provider_data[provider_name]
        target.update(append_data)
        writers.write_yaml(cloud.opts['providers_config'], provider_data)


def bootstrap_master_security_groups(vm_, provider):
    # perhaps run though saltcloud's config look up system?
    # see if the security group is defined on the profile

    app, ssh = initial_security_groups()
    provider_groups = provider.get('securitygroup', [])
    vm_groups = vm_.get('securitygroup', [])

    if isinstance(provider_groups, string_type):
        provider_groups = [provider_groups]

    if isinstance(vm_groups, string_type):
        vm_groups = [vm_groups]

    groups = set(provider_groups).union(vm_groups)

    # Did the user provide their own groups?
    # No matter what, we make our marker security group
    # which is used in locating our cloudseed instances.
    # If the user provided their own groups, the marker
    # will get no ip permissions. Otherwise, we get the
    # group full communication rights to others in the same group

    # no security groups were provided, lets start making our own
    # 1st up is SSH to the new master.
    cloudseed_groups = set()
    exclusions = set()

    if not groups:
        # there is an issue with passing spaces to the salt-cloud
        # query function, so the descriptions contain no spaces.
        # need to figure out if it's on cloudseed's end or salt-cloud's
        ssh_id = create_securitygroup(
            name=ssh,
            description='CloudseedAppSSH')

        if ssh_id:
            authorize_ssh_public(ssh_id)

        cloudseed_groups.add(ssh)
        exclusions.add(ssh)

    if app not in groups:
        # there is an issue with passing spaces to the salt-cloud
        # query function, so the descriptions contain no spaces.
        # need to figure out if it's on cloudseed's end or salt-cloud's
        app_id = create_securitygroup(
            name=app,
            description='CloudseedApp')

        if not groups:
            authorize_all_intragroup(app_id)

        cloudseed_groups.add(app)

    groups = groups.union(cloudseed_groups)

    # need to check if salt-cloud cares if it's exactly a list
    # if it doesn't remove this conversion to list
    vm_['securitygroup'] = list(groups)

    # return all of the groups to be used
    # for the provider, sans the ssh group. You should
    # only be able to ssh into a minon from the master.
    # exclude the groups we found on the vm profile as well
    return list(groups - exclusions.union(vm_groups))


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


def marker_security_group():
    cloud = cloudseed.cloud.Cloud(__opts__)
    vm_ = cloud.vm_profile('master')
    provider = cloud.provider_profile_full(vm_)

    # this should be an array with at LEAST our
    # cloudseed marker in tow if not more, assuming it was
    # bootstrapped through cloudseed
    provider_groups = provider.get('securitygroup', [])

    try:
        # len 3
        # cloudseed-project-env
        return next(x for x in provider_groups
                    if x.startswith('cloudseed') and
                    len(x.split('-')) == 3)
    except StopIteration:
        return None


# def list_nodes_full(location=None):
#     '''
#     Return a list of the VMs that are on the provider
#     This is directly copied from
#     '''
#     if not location:
#         ret = {}
#         locations = set(
#             get_location(vm_) for vm_ in __opts__['vm']
#             if _vm_provider(vm_) == 'ec2'
#         )
#         for loc in locations:
#             ret.update(_list_nodes_full(loc))
#         return ret

#     return _list_nodes_full(location)


def _list_nodes_full(location=None):
    '''
    Return a list of the VMs that in this location
    We only want the nodes that match our marker security group
    '''
    # The only changes from the original _list_nodes_full
    # in saltcloud.clouds.ec2 is the addition of the marker fetch
    # the filters in params and 2 calls to
    # saltcloud.clouds.ec2._extract_name_tag, Otherwise, its the same.
    # The calls to saltcloud.clouds.ec2._extract_name_tag
    # are not different we just have to access the proper function
    # since cloudseed's ec2 module does not define _extract_name_tag

    marker = marker_security_group()

    ret = {}

    # consider fetching the group-id with marker_security_group
    # in addition to the name. VPC instances would need group-id
    #
    # http://docs.aws.amazon.com/AWSEC2/latest/APIReference/ApiReference-query-DescribeInstances.html
    # If the instance is in a nondefault VPC, you must use group-id instead

    params = {
    'Action': 'DescribeInstances',
    'Filter.1.Name': 'group-name',
    'Filter.1.Value.1': marker,
    'Filter.2.Name': 'instance-state-name',
    'Filter.2.Value.1': 'running'}

    instances = query(params, location=location)

    for instance in instances:
        # items could be type dict or list (for stopped EC2 instances)
        if isinstance(instance['instancesSet']['item'], list):
            for item in instance['instancesSet']['item']:
                # calls into original ec2
                name = saltcloud.clouds.ec2._extract_name_tag(item)
                ret[name] = item
                ret[name].update(
                    dict(
                        id=item['instanceId'],
                        image=item['imageId'],
                        size=item['instanceType'],
                        state=item['instanceState']['name'],
                        private_ips=item.get('privateIpAddress', []),
                        public_ips=item.get('ipAddress', [])
                    )
                )
        else:
            item = instance['instancesSet']['item']
            # calls into original ec2
            name = saltcloud.clouds.ec2._extract_name_tag(item)
            ret[name] = item
            ret[name].update(
                dict(
                    id=item['instanceId'],
                    image=item['imageId'],
                    size=item['instanceType'],
                    state=item['instanceState']['name'],
                    private_ips=item.get('privateIpAddress', []),
                    public_ips=item.get('ipAddress', [])
                )
            )
    return ret


saltcloud_ec2_create = saltcloud.clouds.ec2.create
saltcloud.clouds.ec2._list_nodes_full = _list_nodes_full

