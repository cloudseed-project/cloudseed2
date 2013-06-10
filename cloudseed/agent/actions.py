import multiprocessing
import saltcloud.cli


class SaltCloudProfile(multiprocessing.Process):
    def __init__(self, profile, tag):
        self.profile = profile
        self.tag = tag
        #self.stdout = None
        #self.stderr = None
        super(SaltCloudProfile, self).__init__()

    def run(self):
        saltcloud.cli.SaltCloud.parse_args = cloudseed_parse_args
        # saltcloud.cloud.Cloud.create = cloudseed_create
        cloud = saltcloud.cli.SaltCloud()
        cloud.run()

        args = [
        'salt-cloud',
        '-p', self.profile,
        self.tag]

        p = subprocess.Popen(
        args)

        #output, _ = p.communicate()
        #print(output)
        p.wait()
        #retcode = p.poll()

def execute_profile(profile, tag=None):

    log.debug('Bootstrapping profile %s with tag %s', profile, tag)

    action = SaltCloudProfile(profile, tag)
    action.start()
