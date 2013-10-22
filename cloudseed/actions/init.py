import os
from cloudseed.utils.filesystem import symlink
from cloudseed.utils.filesystem import create_default_cloudseed_folders
from cloudseed.utils.salt import create_default_salt_folders
from cloudseed.utils.salt import create_default_salt_files
from cloudseed.utils.vagrant import create_default_vagrant_folders
from cloudseed.utils.vagrant import create_default_vagrant_files


def run(
    path,
    name=None,
    box_id=None,
    box_url=None,
    bridged=False,
    ports=(),
    folders=()):

    create_default_cloudseed_folders()

    if name == 'current':
        raise ValueError('Invalid name, \'%s\' is reserved' % name)

    prefix = os.path.join(path, 'cloudseed', name)
    create_default_salt_folders(prefix)
    create_default_salt_files(prefix)
    create_default_vagrant_folders(prefix)

    create_default_vagrant_files(prefix,
        box=box_id,
        box_url=box_url,
        ports=ports,
        folders=folders,
        bridged=bridged)

    symlink(prefix, os.path.join(path, 'cloudseed', 'current'))
