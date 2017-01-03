import weakref

class Proxy:
    def __init__(self, engine, obj):
        self.obj = weakref.weakref(obj)

    def __getattribute__(self, attr):
        # FIXME: Check for missing object, missing attribute, 
        return getattr(self.obj, attr)
