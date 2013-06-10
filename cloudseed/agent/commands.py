from .utils import master_tunnel


@master_tunnel
def deploy(profile, tag):
    return {'action': 'profile', 'profile': profile, 'tag': 'minion0'}


@master_tunnel
def add_machine(tag, data):
    return {'action': 'add_machine', 'tag': tag, 'data': data}
