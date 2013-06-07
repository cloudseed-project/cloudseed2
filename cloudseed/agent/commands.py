from .utils import master_tunnel



@master_tunnel
def deploy(profile, tag):
    import pdb; pdb.set_trace()
    return {'action': 'profile', 'profile': profile, 'tag': 'minion0'}
