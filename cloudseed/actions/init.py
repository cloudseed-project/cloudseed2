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
    folders=(),
    version='stable',
    forward_agent=True):

    create_default_cloudseed_folders()

    if name == 'current':
        raise ValueError('Invalid name, \'%s\' is reserved' % name)

    prefix = os.path.join(path, 'cloudseed', name)
    create_default_salt_folders(prefix)
    create_default_salt_files(prefix)
    create_default_vagrant_folders(prefix)

    create_default_vagrant_files(prefix,
        name=name,
        box=box_id,
        box_url=box_url,
        ports=ports,
        folders=folders,
        bridged=bridged,
        version=version,
        forward_agent=forward_agent)

    current_path = os.getcwd()
    cloudseed_path = os.path.join(path, 'cloudseed')

    os.chdir(cloudseed_path)
    symlink(name, 'current')
    os.chdir(current_path)
