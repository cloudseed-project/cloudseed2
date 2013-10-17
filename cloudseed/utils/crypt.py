'''
Straight from the salt version
https://github.com/saltstack/salt/blob/develop/salt/crypt.py
'''

import os

#from Crypto.PublicKey import RSA
from M2Crypto import RSA
from Crypto import Random


def gen_keys(keydir, keyname, keysize, user=None):
    '''
    ported to pycrypto per this PR that was accepted but
    not yet merged?
    https://github.com/emonty/salt/commit/3867ffb3efff2df97b4bb82b9fb2afa703786a47

    Generate a keypair for use with salt
    '''
    base = os.path.join(keydir, keyname)
    priv = '{0}.pem'.format(base)
    pub = '{0}.pub'.format(base)

    privkey = RSA.generate(keysize, Random.new().read)
    pubkey = privkey.publickey()

    cumask = os.umask(191)
    with open(priv, 'w') as priv_file:
        priv_file.write(privkey.exportKey())

    os.umask(cumask)
    with open(pub, 'w') as pub_file:
        pub_file.write(pubkey.exportKey())

    os.chmod(priv, 256)
    if user:
        try:
            import pwd
            uid = pwd.getpwnam(user).pw_uid
            os.chown(priv, uid, -1)
            os.chown(pub, uid, -1)
        except (KeyError, ImportError, OSError):
            # The specified user was not found, allow the backup systems to
            # report the error
            pass
    return priv

    base = os.path.join(keydir, keyname)
    priv = '{0}.pem'.format(base)
    pub = '{0}.pub'.format(base)

    gen = RSA.gen_key(keysize, 65537)
    cumask = os.umask(191)
    gen.save_key(priv, None)
    os.umask(cumask)
    gen.save_pub_key(pub)
    os.chmod(priv, 256)
    if user:
        try:
            import pwd
            uid = pwd.getpwnam(user).pw_uid
            os.chown(priv, uid, -1)
            os.chown(pub, uid, -1)
        except (KeyError, ImportError, OSError):
            # The specified user was not found, allow the backup systems to
            # report the error
            pass
    return priv
