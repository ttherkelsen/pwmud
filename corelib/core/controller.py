class controller(load_class("/core/classes/core"), load_class("/core/mixins/global_names")):
    def create(self):
        super().create()

    def init(self): # Engine interface
        # FIXME: preload handlers
        # FIXME: Adjust __builtins__ with overrides and aliases 
        pass

    def global_names(self): # Engine interface
        # Return a list of <str name>, <value> pairs which should be added
        # to the builtins dict and thus be globally available to all
        # objects
        return [ ( t[7:], py.getattr(self, t) ) for t in py.dir(self) if t.startswith('global_') ]
    
    def network_connect(self, raddr, laddr): # Engine interface
        if not self.allow_connect(raddr[0], raddr[1]):
            return None

        return clone_object('/core/connection')


    def allow_connect(self, ip, port):
        # FIXME: Check BAN_H if the ip is banned
        return True



    
