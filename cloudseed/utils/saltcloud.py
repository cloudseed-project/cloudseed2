from __future__ import absolute_import
import os
import logging
import tempfile
import functools
import multiprocessing
#import threading
import saltcloud.cli
from cloudseed.utils import env
from cloudseed.utils import filesystem
import cloudseed.cloud


log = logging.getLogger(__name__)


class SaltCloudProfile(multiprocessing.Process):
# class SaltCloudProfile(threading.Thread):

    @staticmethod
    def _master_parse_args(parse_args, profile, self, args=None, values=None):
        # self will be an instance of saltcloud.cli.SaltCloud
        # we are patching that method
        args = profile.args + ['-p', profile.profile, profile.tag]

        # don't go through self
        parse_args(args, values)

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
        #cloud = cloudseed.cloud.Cloud(self.config)
        #vm_profile = cloud.vm_profile('master')
        #vm_profile['name'] = profile.tag

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

        self.config['deploy_scripts_search_path'] = \
        (cloudseed_deploy_path, ) + deploy_scripts_search_path

    @staticmethod
    def _minion_parse_args(parse_args, profile, self, args=None, values=None):
        args = profile.args + ['-p', profile.profile, profile.tag]

        # don't go through self
        parse_args(args, values)

    def __init__(self, profile, tag, args):
        self.profile = profile
        self.tag = tag
        self.args = args

        #self.stdout = None
        #self.stderr = None
        super(SaltCloudProfile, self).__init__()

    def minon_parse_args(self, args=None, values=None):
        args = self.args + ['-p', self.profile, self.tag]
        self.saltcloud_parse_args(self, args, values)

    def run(self):
        cloud = saltcloud.cli.SaltCloud()

        if self.profile == 'master':
            cloud.parse_args = functools.partial(
                SaltCloudProfile._master_parse_args,
                cloud.parse_args,
                self,
                cloud)
        else:
            cloud.parse_args = functools.partial(
                SaltCloudProfile._minion_parse_args,
                cloud.parse_args,
                self,
                cloud)

        cloud.run()


def execute_profile(profile, tag=None, cloud_config=None, cloud_providers=None,
                    cloud_profiles=None, master_config=None, async=False):

    cloudseed_args = []

    if cloud_config:
        cloudseed_args += ['--cloud-config', cloud_config]

    if cloud_providers:
        cloudseed_args += ['--providers-config', cloud_providers]

    if cloud_profiles:
        cloudseed_args += ['--profiles', cloud_profiles]

    if master_config:
        cloudseed_args += ['--master-config', master_config]

    log.debug('Launching profile %s with tag %s', profile, tag)

    action = SaltCloudProfile(profile, tag, cloudseed_args)

    if async:
        action.start()
    else:
        action.run()
        #action.start()
        #action.join()

    return action



