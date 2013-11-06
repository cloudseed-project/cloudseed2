import logging
import os
import errno

log = logging.getLogger(__name__)


def read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except (OSError, IOError):
        return ''


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST \
        and os.path.isdir(path):
            pass


def symlink(source, link_name):
    try:
        os.unlink(link_name)
    except OSError as e:
        if e.errno == errno.ENOENT:
            pass
        else:
            log.exception(e)

    os_symlink = getattr(os, "symlink", None)

    if callable(os_symlink):
        try:
            os_symlink(source, link_name)
        except OSError as e:
            log.error(
            'Filed to create symlink for %s -> %s',
            source, link_name)
    else:
        # windows compatibility
        # http://stackoverflow.com/questions/6260149/os-symlink-support-in-windows
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            log.error(
            'Filed to create symlink for %s -> %s',
            source, link_name)
            raise ctypes.WinError()


def current_env_path():
    return os.path.join(os.getcwd(), 'cloudseed', 'current')


def resource_path():
    current_path = os.path.join(os.path.dirname(__file__), '../')
    current_path = os.path.normpath(current_path)

    return os.path.join(current_path, 'deploy')


def mkdirs(*args):
    # in py3 map is py2's imap, it won't
    # run until it's iterated over.
    # so we force it.
    any(map(mkdir_p, args))


def create_environment(prefix=''):
    create_default_salt_folders(prefix)


def create_default_cloudseed_folders(prefix=''):
    '''
    Create default cloudseed folders
    '''
    mkdirs(
        # default sls home
        os.path.join(prefix, 'cloudseed')
        )
