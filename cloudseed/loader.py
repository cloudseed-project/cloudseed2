import os
import logging
import salt.loader
import saltcloud.loader
import cloudseed

log = logging.getLogger(__name__)

# Because on the cloud drivers we do `from saltcloud.libcloudfuncs import *`
# which simplifies code readability, it adds some unsupported functions into
# the driver's module scope.
# We list un-supported functions here. These will be removed from the loaded.
LIBCLOUD_FUNCS_NOT_SUPPORTED = (
    'parallels.avail_sizes',
    'parallels.avail_locations',
    'saltify.destroy',
    'saltify.avail_sizes',
    'saltify.avail_images',
    'saltify.avail_locations',
)


def clouds(opts):
    '''
    Return the cloud functions
    '''

    cloudseed_base_path = os.path.dirname(cloudseed.__file__)

    # https://github.com/saltstack/salt/blob/develop/salt/loader.py
    # builds up paths to load
    load = salt.loader._create_loader(
        opts,  # opts
        'clouds',  # ext_type
        '',  # tag - used in creatign ext_type_dirs {0}_dirs for easier extension
        base_path=cloudseed_base_path
    )

    # Let's bring __active_provider_name__, defaulting to None, to all cloud
    # drivers. This will get temporarily updated/overridden with a context
    # manager when needed.
    pack = {
        'name': '__active_provider_name__',
        'value': None
    }

    functions = load.gen_functions(pack)

    for funcname in LIBCLOUD_FUNCS_NOT_SUPPORTED:
        log.debug(
            '{0!r} has been marked as not supported. Removing from the list '
            'of supported cloud functions'.format(
                funcname
            )
        )
        functions.pop(funcname, None)
    return functions

# make sure that cloudseeds clouds are the goto clouds
# which means cloudseed clouds are responsible for importing
# the original saltcloud functions to maintain compatibility
saltcloud.loader.clouds = clouds
