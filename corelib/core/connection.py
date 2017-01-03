class connection(load_class("/core/classes/core")):
    def create(self, *args, **kwargs):
        pass

    def network_connect(self):
        send_message(self, "Hello world!")

    def network_message(self, message): # Engine interface
        pass

    def network_disconnect(self): # Engine interface
        pass
        
