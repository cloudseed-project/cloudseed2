'''
usage:
  cloudseed keys add
  cloudseed keys remove <keyname>

options:
  <environment>         The profile name in your cloudseed/ folder to load
  -h, --help            Show this screen.

'''
import os
import glob
import logging
import hashlib

from docopt import docopt
from cloudseed.utils import salt
from cloudseed.utils import saltcloud
from cloudseed.utils import env
from cloudseed.utils import ssh

from cloudseed.utils.sync import sync_file

log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)

    if args.get('add', False):
        _add_key()


def _add_key():
    user_path = os.path.expanduser('~/.ssh')
    files = glob.glob(os.path.join(user_path, 'id_rsa.pub'))

    if len(files) < 1:
        # TODO ERROR MESSAGES
        return

    target = files[0]
    log.debug('Transferring public key \'%s\' to master', target)
    cloud = env.cloud()

    with open(target, 'rb') as f:
        key_name = hashlib.md5(f.read()).hexdigest()

    sync_file(target, '/tmp/%s' % key_name, cloud)

    client = ssh.master_client(cloud)
    ssh.sudo(
        client,
        'mv /tmp/%s /srv/cloudseed/keys && chmod 600 /srv/cloudseed/keys/%s' % \
        (key_name, key_name))

    salt.sync_key(key_name, client=client)

