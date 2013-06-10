from __future__ import absolute_import
from saltcloud import config
from salt.utils.event import SaltEvent
from cloudseed.utils import ssh
from cloudseed.compat import urlparse
from cloudseed.utils import env


class CloudseedMasterTCPEvent(SaltEvent):
    def __init__(self, node, sock_dir=None, **kwargs):
        kwargs['ipc_mode'] = 'tcp'
        super(CloudseedMasterTCPEvent, self).__init__(node, sock_dir, **kwargs)

    def connect_pull(self):
        '''
        Establish a connection with the event pull socket
        '''

        url = urlparse(self.pulluri)
        host, port = url.netloc.split(':')

        cloud = env.cloud()
        vm_ = cloud.vm_profile('master')

        private_key = config.get_config_value('private_key', vm_, cloud.opts)
        username = config.get_config_value('ssh_username', vm_, cloud.opts)
        password = config.get_config_value('password', vm_, cloud.opts)

        self.push = ssh.agent_zmq_tunnel(
            host=host,
            port=port,
            private_key=private_key,
            username=username,
            password=password)

        #self.push = self.context.socket(zmq.PUSH)
        #self.push.connect(self.pulluri)
        self.cpush = True

