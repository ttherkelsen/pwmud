class connection(load_class("/core/classes/core"), load_class("/core/mixins/terminal")):
    __stages = ( "version", "config", "active" )
    __stage = None
    
    def create(self):
        super().create()

    def network_connect(self):
        # FIXME: Handle timeouts
        log('Connection made')
        self.__stage = 0
        self.handle("network_connect")

    def network_message(self, message): # Engine interface
        log('Incoming: %s' % message)
        self.handle("network_message", message)

    def network_disconnect(self): # Engine interface
        log('Connection lost')     
        self.handle("network_disconnect")

    def handle(self, method, *args):
        try:
            func = py.getattr(self, self.__stages[self.__stage] +"_"+ method)
        except py.AttributeError:
            result = "abort"
        else:
            result = func(*args)
        self.handle_result(result)
        
    def handle_result(self, result):
        py.getattr(self, 'handle_result_'+ result)()
        
    def handle_result_ok(self):
        # Do nothing
        pass

    def handle_result_next(self):
        # Move to next stage
        self.__stage += 1
        self.handle('init')

    def handle_result_abort(self):
        self.abort_connection()

    def abort_connection(self):
        # FIXME: Actually do it
        log('aborting connection due to protocol error')
        pass

    def version_network_connect(self):
        send_message({'type': 'query', 'query': 'version', 'id': self.get_objname()})
        return 'ok'

    def version_network_message(self, message):
        if ( message.get('type') != 'response' 
             or message.get('id') != self.get_objname() 
             or message.get('response') != library_version() ):
            return self.abort_connection()

        return 'next'

    def config_init(self):
        send_message(self.terminal_init('9x15', ('ffffffff', '000000ff'), (80, 40)))
        return 'ok'
