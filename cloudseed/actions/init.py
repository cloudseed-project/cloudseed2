import os
from cloudseed.utils.filesystem import symlink
from cloudseed.utils.filesystem import create_default_cloudseed_folders
from cloudseed.utils.salt import create_default_salt_folders
from cloudseed.utils.salt import create_default_salt_files
from cloudseed.utils.vagrant import create_default_vagrant_folders
from cloudseed.utils.vagrant import create_default_vagrant_files
from cloudseed import forms


def run(
    path,
    name=None,
    box_id=None,
    os_id=None,
    ports=(),
    bridged=False):

    results = forms.init.run(
        name=name,
        box_id=box_id,
        os_id=os_id,
        ports=ports)

    import pdb; pdb.set_trace()

    create_default_cloudseed_folders()

    if results['name'] == 'current':
        raise ValueError('Invalid name, \'%s\' is reserved' % results['name'])

    prefix = os.path.join(path, 'cloudseed', name)
    create_default_salt_folders(prefix)
    create_default_salt_files(prefix)
    create_default_vagrant_folders(prefix)

    create_default_vagrant_files(prefix,
        box=results['box_id'],
        box_url=results['box_url'],
        ports=results['ports'],
        bridged=bridged)

    symlink(prefix, os.path.join(path, 'cloudseed', 'current'))
