class connection(load_class("/core/classes/core")):
    def create(self, *args, **kwargs):
        pass

    def network_connect(self):
        send_message("Hello world!")

    def network_message(self, message): # Engine interface
        py.print('Connection obj %s network_message:' % self.get_objname(), message)
        send_message({'type': 'init', 'message': 'You sent: %s' % message})

    def network_disconnect(self): # Engine interface
        py.print('Connection obj %s network_disconnect' % self.get_objname())
        
