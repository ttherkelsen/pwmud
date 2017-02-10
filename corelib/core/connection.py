class connection(load_class("/core/classes/core")):
    def create(self, *args, **kwargs):
        pass

    def network_connect(self):
        log('Connection made')

    def network_message(self, message): # Engine interface
        log('Incoming: %s' % message)
        send_message({'type': 'init', 'message': 'You sent: %s' % message})

    def network_disconnect(self): # Engine interface
        log('Connection lost')      
