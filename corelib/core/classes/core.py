class core:
    # objname is a compromise; the engine only maintains a mapping
    # from objname to actual Python object, it does not maintain the
    # inverse.  Now, we could search through the objects dict to find
    # the objname from the object.  You could also have the engine
    # maintain an object-to-objname mapping.  The solution I chose was
    # to let each object know its own objname, and then letting the
    # code that needs this information rely on retrieving it from the
    # object.  The value of this attribute is set from the engine's
    # object instantiation mechanisms (eg., load_object()) via
    # __init__() before create() has been called, so it is safe to
    # rely on it from create().
    __objname = None

    # No other class should define __init__ than the core object
    def __init__(self, objname, origin):
        # objname is the name I have in the engine backend
        # origin is the name of the efun that created me
        self.__objname = objname

    def get_objname(self): return self.__objname
    
    def create(self):
        pass
