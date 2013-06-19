import os
import salt.loader
import cloudseed


def clouds(opts):
    '''
    Return the cloud functions
    '''
    # https://github.com/saltstack/salt/blob/develop/salt/loader.py
    # builds up paths to load
    load = salt.loader._create_loader(
        opts,  # opts
        'clouds',  # ext_type
        '',  # tag - used in creatign ext_type_dirs {0}_dirs for easier extension
        base_path=os.path.dirname(
            cloudseed.__file__
        )
    )

    # Let's bring __active_provider_name__, defaulting to None, to all cloud
    # drivers. This will get temporarily updated/overridden with a context
    # manager when needed.
    pack = {
        'name': '__active_provider_name__',
        'value': None
    }

    functions = load.gen_functions(pack)

    return functions
