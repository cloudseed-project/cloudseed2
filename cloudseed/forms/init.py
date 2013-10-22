from itertools import chain
from promptly import Form
from cloudseed.utils import data
from cloudseed.compat import iterkeys


def run(name=None,
    box_id=None,
    os_id=None,
    ports=()):

    available_boxes = data.fetch_boxes()
    available_ports = data.fetch_ports()

    form = build_form(
        name=name,
        box_id=box_id,
        os_id=os_id,
        ports=ports,
        data_boxes=available_boxes,
        data_ports=available_ports)

    if len(form) == 0:
        return

    form.run(prefix=None)

    # Form Results
    results = dict(form)
    #####

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

    results.update({
        'name': results.get('name', name),
        'box_id': key_box,
        'os_id': key_os,
        'box_url': available_boxes[key_os][key_box]['url'],
        'ports': selected_ports
        })

    return results


def build_form(
    name='default',
    box_id=None,
    os_id=None,
    ports=(),
    data_boxes={},
    data_ports={}):

    form = Form()

    if not name:
        form.add.string('name',
            'Provide a name for this environment',
            default='default')

    if not box_id or not os_id and data_boxes:
        choices = sorted(tuple(iterkeys(data_boxes)))
        form.add.select('os_id', 'Choose your Operating System',
            choices, default=1)

        form.add.branch(build_branch, boxes=data_boxes)

    if not ports and data_ports:
        form.add.multiselect('ports',
            'Choose ports you would like to forward',
            sorted(iterkeys(data_ports)))

    return form


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


