class core:
    # _objname is a compromise; the engine only maintains a mapping
    # from objname to actual Python object, it does not maintain the
    # inverse.  Now, we could search through the objects dict to find
    # the objname from the object.  You could also have the engine
    # maintain an object-to-objname mapping.  The solution I chose was
    # to let each object know its own objname, and then letting the
    # code that needs this information (such as proxy()) rely on
    # retrieving it directly from the object.  The value of this
    # attribute is set from the engine's object instantiation
    # mechanisms (eg., load_object()) before create() has been called,
    # so it is safe to rely on it from create().
    _objname = None

    def __init__(self, *args, **kwargs):
        pass

    def create(self):
        pass
