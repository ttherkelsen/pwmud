class connection(load_class("/core/classes/core")):
    def create(self):
        send_message("Hello world!")

    def network_message(self, message): # Engine interface
        pass

    def network_disconnect(self): # Engine interface
        pass
        
