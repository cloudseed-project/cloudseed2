'''
usage:
  cloudseed bootstrap <environment>

options:
  <environment>         The profile name in your cloudseed/ folder to load
  -h, --help            Show this screen.

'''
import saltcloud.cli


saltcloud_parse_args = saltcloud.cli.SaltCloud.parse_args


def run(argv):
    saltcloud.cli.SaltCloud.parse_args = cloudseed_parse_args
    cloud = saltcloud.cli.SaltCloud()
    cloud.run()


def cloudseed_parse_args(self, args=None, values=None):
    saltcloud_parse_args(self, ['-y', '-p' 'master', 'master'], values)
    try:
        provider = [x['provider'] for x in self.config['vm']
                    if x['profile'] == 'master'][0]
    except IndexError:
        raise  # profile does not exist

    try:
        providers = self.config['providers'][provider]
    except KeyError:
        raise  # provider does not exist

    [x.__setitem__('ssh_interface', 'public_ips') for x in providers]

    #import pdb; pdb.set_trace()
    #foo =1
    #[y['ssh_interface'] = 'public_ips' for x in  for y in x]

    # options, args = optparse.OptionParser.parse_args(
    #     self, ['-p' 'master', 'master'], values)

    #self.options, self.args = options, args


