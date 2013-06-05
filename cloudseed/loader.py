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

    functions = load.gen_functions()

    return functions
