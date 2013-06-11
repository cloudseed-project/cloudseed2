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
            'master': {'machines': [data]}
        }

        self.collection.save(base)

    def add_machine(self, tag, data):
        self.collection.update(
            {'_id': 'cloudseed'},
            {'$push': {'%s.machines' % tag: data}}
        )

    def data(self):
        return self.collection.find_one({'_id': 'cloudseed'})
