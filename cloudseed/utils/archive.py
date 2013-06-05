import os
import itertools
import tarfile
import hashlib
from cloudseed.compat import string_type


class Archive(object):

    @staticmethod
    def tar(filename, manifest):

        if isinstance(filename, string_type):
            archive = tarfile.open(filename, mode='w:gz')
            to_close = (archive, )
        else:
            archive = tarfile.open(fileobj=filename, mode='w:gz')
            to_close = (archive, filename)

        def write(origin, target, kind):
            if kind == 'fileobj':
                origin.seek(0, os.SEEK_END)
                info = tarfile.TarInfo(name=target)
                info.size = origin.tell()
                origin.seek(0)
                archive.addfile(tarinfo=info, fileobj=origin)
            else:
                archive.add(origin, target)

        any(itertools.starmap(write, manifest))
        [x.close() for x in to_close]


class Manifest(object):
    def __init__(self):
        self.locations = set()
        self.objs = {}

    def add(self, name, target=None):

        if isinstance(name, string_type):
            kind = 'filename'
            if not os.path.isabs(name):
                origin = os.path.abspath(name)
            else:
                origin = name
        else:
            kind = 'fileobj'
            name.seek(0)
            origin = hashlib.md5(name.read()).hexdigest()
            self.objs[origin] = name

        if not target:
            target = name

        self.locations.add((origin, target, kind))

    def remove(self, name):
        if isinstance(name, string_type):
            if not os.path.isabs(name):
                target = os.path.abspath(name)
            else:
                target = name
        else:
            name.seek(0)
            target = hashlib.md5(name.read()).hexdigest()

        # if we have 2 items in the locations set that have the same
        # origin but different targets, this will not work. It will just
        # be the 1st result, which may not be correct.
        #
        # Suggestion: remove, like add can take 2 arguments, the second
        # being target, and treat it the same as add does.
        # It may never be an issue, so letting it ride for now.
        match = next((x for x in self.locations if x[0] == target), None)

        try:
            self.locations.remove(match)
        except KeyError:
            pass

        if match[2] == 'fileobj':
            del self.objs[target]

    def __iter__(self):
        for each in self.locations:
            if each[2] == 'fileobj':
                yield self.objs[each[0]], each[1], each[2]
            else:
                yield each

