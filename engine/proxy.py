class Proxy:
    def __init__(self, engine, objname):
        object.__setattr__(self, 'engine', engine)
        object.__setattr__(self, 'objname', objname)

    def __getattribute__(self, attr):
        # FIXME: Check for missing object, missing attribute,
        # don't allow access to anything that's non-callable or
        # starts with "_"
        return getattr(self.engine.objects[object.__getattribute__(self, 'objname')], attr)

    def __setattr__(self, attr, value):
        raise NotImplementedError

    def __delattr__(self, attr, value):
        raise NotImplementedError
