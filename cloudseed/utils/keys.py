import os
import shutil
import tempfile
from . import crypt

try:
    import fcntl
    HAS_FNCTL = True
except ImportError:
    # fcntl is not available on windows
    HAS_FNCTL = False


def fopen(*args, **kwargs):
    '''
    Taken from salt.utils.__init__.py
    https://github.com/saltstack/salt/blob/develop/salt/utils/__init__.py#L926-L946

    Wrapper around open() built-in to set CLOEXEC on the fd.

    This flag specifies that the file descriptor should be closed when an exec
    function is invoked;
    When a file descriptor is allocated (as with open or dup ), this bit is
    initially cleared on the new file descriptor, meaning that descriptor will
    survive into the new program after exec.
    '''
    fhandle = open(*args, **kwargs)
    if HAS_FNCTL:
        # modify the file descriptor on systems with fcntl
        # unix and unix-like systems only
        try:
            FD_CLOEXEC = fcntl.FD_CLOEXEC   # pylint: disable=C0103
        except AttributeError:
            FD_CLOEXEC = 1                  # pylint: disable=C0103
        old_flags = fcntl.fcntl(fhandle.fileno(), fcntl.F_GETFD)
        fcntl.fcntl(fhandle.fileno(), fcntl.F_SETFD, old_flags | FD_CLOEXEC)
    return fhandle


def gen_keys(keysize=2048):
    '''
    Taken from saltcloud.utils.__init__.py
    https://github.com/saltstack/salt-cloud/blob/develop/saltcloud/utils/__init__.py#L98-L115

    Generate Salt minion keys and return them as PEM file strings
    '''
    # Mandate that keys are at least 2048 in size
    if keysize < 2048:
        keysize = 2048
    tdir = tempfile.mkdtemp()

    crypt.gen_keys(tdir, 'minion', keysize)
    priv_path = os.path.join(tdir, 'minion.pem')
    pub_path = os.path.join(tdir, 'minion.pub')
    with fopen(priv_path) as fp_:
        priv = fp_.read()
    with fopen(pub_path) as fp_:
        pub = fp_.read()
    shutil.rmtree(tdir)
    return priv, pub
