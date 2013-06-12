'''
{
    'env': 'sample.foo',
    'master': {
        'machines': [
            {'ip_address': data['ipAddress'],
             'dns_name': data['dnsName'],
             'private_ip_address': data['privateIpAddress'],
             'status': 'running',
             'instance_id': 'i-130c9168'
            },
        ]
    }
    'django':{
        'machines': [
            {'ip_address': data['ipAddress'],
             'dns_name': data['dnsName'],
             'private_ip_address': data['privateIpAddress'],
             'status': 'running',
             'instance_id': 'i-130c9168'
            },

            {'ip_address': data['ipAddress'],
             'dns_name': data['dnsName'],
             'private_ip_address': data['privateIpAddress'],
             'status': 'running',
             'instance_id': 'i-130c9168'
            }
        ]
    }
}
'''
from pymongo import MongoClient


class MongoResource(object):
    def __init__(self):
        self.client = MongoClient('localhost')
        self.db = self.client.cloudseed
        self.collection = self.db.status

    def init_cloudseed(self, data):
        base = {
            '_id': 'cloudseed',
            'seq': -1,
            'machines': {
                'master': [data]
            }
        }

        self.collection.save(base)

    def add_machine(self, tag, data):
        self.collection.update(
            {'_id': 'cloudseed'},
            {'$push': {'machines.%s' % tag: data}}
        )

    def manifest(self):
        return self.collection.find_one({'_id': 'cloudseed'})

    def machines(self):
        data = self.manifest()
        return data['machines']

    def next_seq(self):
        # not really what we need as this seems to be per document.
        # Adding here for reference in case it comes up.
        # http://docs.mongodb.org/manual/tutorial/create-an-auto-incrementing-field/

        self.collection.update(
            {'_id': 'cloudseed'},
            {'$inc': {'seq': 1}}
        )

        data = self.manifest()
        return data['seq']
