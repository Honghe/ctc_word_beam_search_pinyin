import collections


def packKey(l):
    return '_'.join([str(i) for i in l])


def unpackKey(k):
    return [int(i) for i in k.split('_')]


class TransformedDict(collections.MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys
       d = TransformedDict([])
       对int list隐式转成str key"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        # preprocess
        if type(key) is list:
            key = packKey(key)
        return key

    def keys(self):
        keys = self.store.keys()
        return [unpackKey(i) for i in keys if type(i) is not list]

    def __repr__(self):
        return '{' + ''.join(["'{}': {},".format(k, self.__getitem__(k)) for k in self.__iter__()]) + '}'
