from .utils import master_tunnel



@master_tunnel
def deploy(profile, tag):
    return {'action': 'profile', 'profile': profile, 'tag': 'minion0'}
