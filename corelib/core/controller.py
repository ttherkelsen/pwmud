class controller(load_class("/core/classes/core")):
    def create(self, *args, **kwargs):
        super().create(*args, **kwargs)

    def init(self): # Engine interface
        # FIXME: preload handlers
        # FIXME: Adjust __builtins__ with overrides and aliases 
        pass

    def connect(self, raddr, laddr): # Engine interface
        if not self.allow_connect(raddr[0], raddr[1]):
            return None

        return clone_object('/core/connection')


    def allow_connect(self, ip, port):
        # FIXME: Check BAN_H if the ip is banned
        return True



    
