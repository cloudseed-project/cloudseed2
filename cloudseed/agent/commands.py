from .utils import master_tunnel


@master_tunnel
def deploy(profile, tag):
    return {'action': 'profile', 'profile': profile, 'tag': tag}


@master_tunnel
def fire_event(data):
    return {'action': 'event', 'data': data}


@master_tunnel
def status():
    return {'action': 'status'}
