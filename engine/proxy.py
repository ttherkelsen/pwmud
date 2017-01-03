class Proxy:
    def __init__(self, engine, objname):
        self.engine = engine
        self.objname = objname

    def __getattribute__(self, attr):
        # FIXME: Check for missing object, missing attribute,
        # don't allow access to anything that's non-callable or
        # starts with "_"
        return getattr(self.engine.objects[self.objname], attr)
