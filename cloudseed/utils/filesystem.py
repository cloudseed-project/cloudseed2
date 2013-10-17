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

    try:
        os.symlink(source, link_name)
    except OSError as e:
        log.error(
            'Filed to create symlink for %s -> %s',
            source, link_name)


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
