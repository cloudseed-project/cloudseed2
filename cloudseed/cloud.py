from saltcloud.cloud import Cloud
import cloudseed.loader


class Cloud(Cloud):

    def __init__(self, opts):
        # override init or else the saltcloud loader will
        # be engaged loading in all of the saltcloud clouds
        self.opts = opts
        self.clouds = cloudseed.loader.clouds(opts)

    def provider_profile_full(self, vm_):

        alias, driver = self.lookup_providers(vm_['provider'])
        providers = self.opts['providers']

        data = providers.get(alias, {})
        target = data.get(driver, {})
        return target

    def vm_profile(self, name):
        try:
            return self.opts['profiles'][name]
        except KeyError:
            # TODO need a better Error, for now, just
            # re raise so we die
            raise  # profile does not exist
