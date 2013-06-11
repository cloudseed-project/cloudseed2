class CloudseedService(object):

    def __init__(self, resource):
        self.resource = resource

    def init_cloudseed(self, data):
        self.resource.init_cloudseed(data)

    def add_machine(self, tag, data):
        self.resource.add_machine(tag, data)

    def data(self):
        return self.resource.data()
