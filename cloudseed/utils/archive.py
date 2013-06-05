import os
from collections import namedtuple
import itertools
import tarfile

_Location = namedtuple('_Location', ['origin', 'target'])


class Archive(object):

    @staticmethod
    def tar(filename, manifest):
        # PY3K Broken
        if isinstance(filename, basestring):
            archive = tarfile.open(filename, mode='w:gz')
            to_close = [archive]
        else:
            archive = tarfile.open(fileobj=filename, mode='w:gz')
            to_close = [archive, filename]

        def write(origin, target):
            archive.add(origin, target)

        any(itertools.starmap(write, manifest))
        [x.close() for x in to_close]


class Manifest(object):
    def __init__(self):
        self.locations = []

    def add(self, name, target=None):

        if not os.path.isabs(name):
            origin = os.path.abspath(name)
        else:
            origin = name

        if not target:
            target = name

        self.locations.append((origin, target))

    def __iter__(self):
        return iter(self.locations)

