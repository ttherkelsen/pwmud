import argparse, os.path, sys, traceback, json

import network.loop, errors, file_adapters

# Efun imports

class Engine(object):
    version = 'PWMud 0.1a'
    class config: pass

    def __init__(self, config_file):
        self.config_file = config_file

        class Proxy:
            engine = self
            def __init__(self, objname):
                self.objname = objname

            def __getattribute__(self, attr):
                # FIXME: Check for missing object, missing attribute,
                # don't allow access to anything that's non-callable or
                # starts with "_"
                return getattr(self.engine.objects[self.objname], attr)
        self.Proxy = Proxy

    def setup(self):
        self.objects = {}
        self.classes = {}
        self.builtins = {
            '__build_class__': __builtins__.__build_class__,
            '__name__': 'engine',
            'py': __builtins__,
            
            'load_class': self.efun_load_class,
            'clone_object': self.efun_clone_object,
        }
        self.connections = {}
        self.guid = 0

    def run(self):
        self.setup()
        self.load_config()
        self.load_object(self.config.controller)

        self.objects[self.config.controller].init()
        network.loop.run(self)

    def cmd_version(self):
        print(self.version)
        sys.exit()

    def next_guid(self):
        self.guid += 1
        return self.guid
        
    def execute_file(self, fn, code, globals=None, locals=None):
        try:
            exec(code, globals, locals)
        except SyntaxError as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            line_number = err.lineno
        except Exception as err:
            error_class = err.__class__.__name__
            detail = err.args[0]
            cl, exc, tb = sys.exc_info()
            line_number = traceback.extract_tb(tb)[-1][1]
        else:
            return
        raise errors.ExecError("%s at line %d of %s: %s" % (error_class, line_number, fn, detail))

    def load_config(self):
        env = {}

        # Add file adapters to the env so the config file can use them
        for name in dir(file_adapters):
            if name.startswith('_'):
                continue
            
            value = getattr(file_adapters, name)
            try:
                if issubclass(value, file_adapters.FileAdapter):
                    env[name] = value
            except:
                pass

        with open(self.config_file, 'r') as fd:
            code = fd.read()
            
        self.execute_file(self.config_file, code, env)
        
        for k, v in env.items():
            if k.startswith('_'):
                continue
            setattr(self.config, k, v)

            
    def load_file(self, pwmfn):
        last_error = None
        for fa in self.config.file_adapters:
            try:
                return fa.load_file(pwmfn)
            except (errors.InvalidPath, errors.FileNotFound) as err:
                last_error = err
        raise last_error

    def save_file(self, pwmfn, data):
        last_error = None
        for fa in self.config.file_adapters:
            try:
                return fa.save_file(pwmfn, data)
            except (errors.InvalidPath, errors.FileNotFound) as err:
                last_error = err
        raise last_error


    def load_class(self, pwmfn):
        if pwmfn not in self.classes:
            env = { '__builtins__': self.builtins }
            far = self.load_file(pwmfn +".py")
            cls = far.basename()[:-3]
            self.execute_file(far.path, far.data, env)
            if cls not in env or not isinstance(env[cls], type):
                # FIXME: This causes the wrong linenum in the traceback error
                raise errors.ClassNotFound("file '%s' does not contain a class named '%s'" % (pwmfn, cls))
            self.classes[pwmfn] = env[cls]
            
        return self.classes[pwmfn]

    def load_object(self, pwmfn):
        # FIXME: Should loaded object also have GUID?
        if pwmfn not in self.objects:
            cls = self.load_class(pwmfn)
            obj._objname = pwmfn
            obj = cls()
            self.objects[pwmfn] = obj

        return self.objects[pwmfn]
        
    def clone_object(self, pwmfn):
        cls = self.load_class(pwmfn)
        obj = cls()
        objname = pwmfn +"#"+ self.next_guid()
        obj._objname = objname
        obj.create()
        self.objects[objname] = obj
        return obj

    def proxy(self, obj):
        # obj can be an actual Python instantiated class or a string
        # if obj is a string, we take it as is
        # if obj is an object, we assume it has the core class as one
        # of its ancestors and we use obj._objname to retrieve the name
        # of the object
        # FIXME: This has to be guarded against errors, of course
        if type(obj) is str:
            return self.Proxy(obj)

        return self.Proxy(obj._objname)
    
    def efun_load_class(self, path):
        return self.load_class(path)

    def efun_clone_object(self, path):
        return self.proxy(self.clone_object(path))

    def efun_proxy(self, obj):
        self.proxy(obj)

    def network_connect(self, handler):
        socket = handler.transport.get_extra_info('socket')
        print(socket.fileno(), socket.getpeername(), socket.getsockname())
        # FIXME: ask the controller object for a connection object
        self.connections[socket.fileno()] = 1 # FIXME: Should be name of object

    def network_disconnect(self, handler):
        # FIXME: tell the connection object that it was disconnected and it no
        # longer interactive, if it exists
        socket = handler.transport.get_extra_info('socket')
        del self.connections[socket.fileno()]

    def network_message(self, message, handler):
        print("Engine: Received message:", message)
        handler.send_message({'type': 'init', 'message': 'You sent: %s' % message})

    def housekeeping(self):
        # The first time this is called is actually just before the network loop is started
        #print("Housekeeping called")
        pass
        

if __name__ == '__main__':
    # FIXME: Setup logging module so it can be used instead of prints everywhere
    cmdline = argparse.ArgumentParser(description="Run a PWMud.")
    cmdline.add_argument('-v', '--version', action="store_true", default=False, help='Print version and exit.')
    cmdline.add_argument('config', help='Path to config file')
    args = cmdline.parse_args()

    engine = Engine(args.config)
    if args.version:
        engine.cmd_version()
    engine.run()

