'''
usage:
  cloudseed init [options] [(--os=<os> --box=<box>)][--port=<port>...]

options:
  -n <name>, --name=<name>  Name of the environment to initialize [default: default]
  -o <os>, --os=<os>        OS id to use
  -b <box>, --box=<box>     Box id to use
  -p <port>, --port=<port>  Enable port forwarding for the specified ports.
  -g, --bridge              Enable Bridged Networking
  -h, --help                Show this screen.


'''
import os
from itertools import chain
import logging
from docopt import docopt
from promptly import Form
from cloudseed.utils.filesystem import symlink
from cloudseed.utils.filesystem import create_default_cloudseed_folders
from cloudseed.utils.salt import create_default_salt_folders
from cloudseed.utils.salt import create_default_salt_files
from cloudseed.utils.vagrant import create_default_vagrant_folders
from cloudseed.utils.vagrant import create_default_vagrant_files
from cloudseed.utils import data
from cloudseed.compat import iterkeys

log = logging.getLogger(__name__)


def run(argv):
    args = docopt(__doc__, argv=argv)
    init(name=args['--name'],
         os_id=args['--os'],
         box_id=args['--box'],
         ports=args['--port'],
         bridged=args['--bridge'])

    print('Cloudseed initialized')


def init(name=None, os_id=None, box_id=None, ports=None, bridged=False):
    selected_ports = None
    key_os = None
    key_box = None
    box_url = None

    available_boxes = data.fetch_boxes()
    available_ports = data.fetch_ports()

    form = Form()

    if not name:
        form.add.string('name',
            'Provide a name for this environment',
            default='default')

    if not box_id or not os_id:
        choices = sorted(tuple(iterkeys(available_boxes)))
        form.add.select('os_id', 'Choose your Operating System',
            choices, default=1)

        form.add.branch(build_branch, boxes=available_boxes)

    if not ports:
        form.add.multiselect('ports',
            'Choose ports you would like to forward',
            sorted(iterkeys(available_ports)))

    # run the form if we are missing information from the
    # command line arguments
    if len(form):
        form.run(prefix=None)
        results = dict(form)

        if 'os_id' in results:
            key_os = form.os_id.value[1]
            key_box, _ = form.box_id.value[1].split(' ', 1)

        if 'ports' in results:
            port_map = form.ports.value

            def map_action(value):
                _, key = value
                ports = available_ports[key]
                return [{'port': x['port'],
                         'label': '%s %s' % (key.lower(), x.get('label', ''))}
                         for x in ports]

            selected_ports = list(chain(
                *map(map_action, port_map))
            )

    # the user could pass in any case, lets normalize it for our search
    # command line options override any for selected options
    if os_id and box_id:
        try:
            key_os = next(x for x in iterkeys(available_boxes) if x.lower() == os_id.lower())
            key_box = next(x for x in iterkeys(available_boxes[key_os]) if x.lower() == box_id.lower())
        except StopIteration:
            raise ValueError
    if ports:
        selected_ports = [{'port': x} for x in ports]

    box_url = available_boxes[key_os][key_box]['url']

    create_default_cloudseed_folders()

    if name == 'current':
        print('Invalid name, \'current\' is reserved.')
        return

    cwd = os.getcwd()
    prefix = os.path.join(cwd, 'cloudseed', name)
    create_default_salt_folders(prefix)
    create_default_salt_files(prefix)
    create_default_vagrant_folders(prefix)

    create_default_vagrant_files(prefix,
        box=key_box,
        box_url=box_url,
        ports=selected_ports,
        bridged=bridged)

    symlink(prefix, os.path.join(cwd, 'cloudseed', 'current'))


def build_branch(form, boxes):
    _, label = form.os_id.value

    ctx = boxes.get(label, {})
    keys = tuple(iterkeys(ctx))
    choices = ['%s [%s]' % (x, ctx[x]['label']) for x in keys]

    branch = Form()
    branch.add.select(
        'box_id',
        'Choose Virtual Machine Image for %s' % label,
        choices, default=1)

    return branch

