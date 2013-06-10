class CloudseedService(object):

    def __init__(self, resource):
        self.resource = resource

    def init_service(self, env):
        self.resource.init_service(env)

    def add_machine(self, tag, data):
        self.resource.add_machine(tag, data)
