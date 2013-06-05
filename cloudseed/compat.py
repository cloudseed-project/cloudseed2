import sys
_ver = sys.version_info

is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)

if is_py2:
    from cStringIO import StringIO
    string_type = basestring
    iterkeys = dict.iterkeys

elif is_py3:
    from io import StringIO
    string_type = str
