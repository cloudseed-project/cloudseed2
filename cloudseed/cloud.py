from saltcloud.cloud import Cloud
import cloudseed.loader


class Cloud(Cloud):

    def __init__(self, opts):
        # override init or else the saltcloud loader will
        # be engaged loading in all of the saltcloud clouds
        self.opts = opts
        self.clouds = cloudseed.loader.clouds(opts)

    def provider_profile_full(self, vm_):
        provider = vm_['provider']

        if ':' in provider:
            # We have the alias and the provider
            # Return the provider
            alias, provider = provider.split(':')
            provider

        if provider in self.opts['providers']:
                return self.opts['providers'][provider][0]

    def vm_profile(self, name):
        try:
            return [x for x in self.opts['vm']
                    if x['profile'] == name][0]
        except IndexError:
            # TODO need a better Error, for now, just
            # re raise so we die
            raise  # profile does not exist
