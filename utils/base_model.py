import UserDict
from _weakref import ref

__all__ = ["Base"]


def __declarative_constructor(self, **kwargs):
    """A simple constructor that allows initialization from kwargs.

    Sets attributes on the constructed instance using the names and
    values in ``kwargs``.

    Only keys that are present as
    attributes of the instance's class are allowed. These could be,
    for example, any mapped columns or relationships.
    """
    cls_ = type(self)
    for k in kwargs:
        if not hasattr(cls_, k):
            raise TypeError(
                "%r is an invalid keyword argument for %s" %
                (k, cls_.__name__))
        setattr(self, k, kwargs[k])
__declarative_constructor.__name__ = '__init__'


class __WeakValueDictionary(UserDict.UserDict):
    def __init__(self, *args, **kw):
        def remove(wr, selfref=ref(self)):
            self = selfref()
            if self is not None:
                del self.data[wr.key]
        self._remove = remove
        UserDict.UserDict.__init__(self, *args, **kw)

    def __getitem__(self, key):
        o = self.data[key]()
        if o is None:
            raise KeyError, key
        else:
            return o

    def __contains__(self, key):
        try:
            o = self.data[key]()
        except KeyError:
            return False
        return o is not None

    def has_key(self, key):
        try:
            o = self.data[key]()
        except KeyError:
            return False
        return o is not None

    def __repr__(self):
        return "<WeakValueDictionary at %s>" % id(self)

    def __setitem__(self, key, value):
        self.data[key] = __KeyedRef(value, self._remove, key)

    def copy(self):
        new = __WeakValueDictionary()
        for key, wr in self.data.items():
            o = wr()
            if o is not None:
                new[key] = o
        return new

    __copy__ = copy

    def __deepcopy__(self, memo):
        from copy import deepcopy
        new = self.__class__()
        for key, wr in self.data.items():
            o = wr()
            if o is not None:
                new[deepcopy(key, memo)] = o
        return new

    def get(self, key, default=None):
        try:
            wr = self.data[key]
        except KeyError:
            return default
        else:
            o = wr()
            if o is None:
                return default
            else:
                return o

    def items(self):
        L = []
        for key, wr in self.data.items():
            o = wr()
            if o is not None:
                L.append((key, o))
        return L

    def iteritems(self):
        for wr in self.data.itervalues():
            value = wr()
            if value is not None:
                yield wr.key, value

    def iterkeys(self):
        return self.data.iterkeys()

    def __iter__(self):
        return self.data.iterkeys()

    def itervaluerefs(self):
        return self.data.itervalues()

    def itervalues(self):
        for wr in self.data.itervalues():
            obj = wr()
            if obj is not None:
                yield obj

    def popitem(self):
        while 1:
            key, wr = self.data.popitem()
            o = wr()
            if o is not None:
                return key, o

    def pop(self, key, *args):
        try:
            o = self.data.pop(key)()
        except KeyError:
            if args:
                return args[0]
            raise
        if o is None:
            raise KeyError, key
        else:
            return o

    def setdefault(self, key, default=None):
        try:
            wr = self.data[key]
        except KeyError:
            self.data[key] = __KeyedRef(default, self._remove, key)
            return default
        else:
            return wr()

    def update(self, dict=None, **kwargs):
        d = self.data
        if dict is not None:
            if not hasattr(dict, "items"):
                dict = type({})(dict)
            for key, o in dict.items():
                d[key] = __KeyedRef(o, self._remove, key)
        if len(kwargs):
            self.update(kwargs)

    def valuerefs(self):
        return self.data.values()

    def values(self):
        L = []
        for wr in self.data.values():
            o = wr()
            if o is not None:
                L.append(o)
        return L

class __KeyedRef(ref):
    """Specialized reference that includes a key corresponding to the value.

    This is used in the WeakValueDictionary to avoid having to create
    a function object for each key stored in the mapping.  A shared
    callback object can use the 'key' attribute of a KeyedRef instead
    of getting a reference to the key from an enclosing scope.

    """

    __slots__ = "key",

    def __new__(type, ob, callback, key):
        self = ref.__new__(type, ob, callback)
        self.key = key
        return self

    def __init__(self, ob, callback, key):
        super(__KeyedRef,  self).__init__(ob, callback)

class __DeclarativeMeta(type):
    def __init__(cls, classname, bases, dict_):
        # if '_decl_class_registry' not in cls.__dict__:
            # _as_declarative(cls, classname, cls.__dict__)
        type.__init__(cls, classname, bases, dict_)

    def __setattr__(cls, key, value):
        if '__mapper__' in cls.__dict__:
            type.__setattr__(cls, key, value)
        else:
            type.__setattr__(cls, key, value)


__bases = not isinstance(object, tuple) and (object,) or object
__dictionary = __WeakValueDictionary()
__class_dict = dict(_decl_class_registry=__dictionary)
__class_dict['__init__'] = __declarative_constructor

BaseModel = __DeclarativeMeta('Base', __bases, __class_dict)

def test():
    class A(Base):
        name = None
    a = A(name="zhipeng")
    print a.name

    print "--------------"

    b = A()
    b.name="zhang"
    print b.name

if __name__ == '__main__':
    test()
