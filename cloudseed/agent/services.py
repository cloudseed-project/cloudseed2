class CloudseedService(object):

    def __init__(self, resource):
        self.resource = resource

    def init_cloudseed(self, data):
        self.resource.init_cloudseed(data)

    def add_machine(self, tag, data):
        self.resource.add_machine(tag, data)

    def next_seq(self):
        self.resource.next_seq()

    def machines(self):
        return self.resource.machines()
