import argparse, os.path, sys, traceback, json, inspect

import network.loop, errors, file_adapters

# Efun imports

class Engine(object):
    version = 'PWMud 0.1a'
    class config: pass

    def __init__(self, config_file):
        self.config_file = config_file

    def setup(self):
        self.objects = {}
        self.classes = {}
        self.builtins = {
            '__build_class__': __builtins__.__build_class__,
            'py': __builtins__,
            'super': __builtins__.super,
            '__name__': 'engine',
            
            'load_class': self.efun_load_class,
            'clone_object': self.efun_clone_object,
            'load_object': self.efun_load_object,
            'send_message': self.efun_send_message,
            
        }
        self.connections = {}
        self.guid = 0
        self.object_stack = []

    def run(self):
        self.setup()
        self.load_config()
        self.load_object(self.config.controller)

        self.start_call(self.config.controller, 'init')
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
            obj = cls(pwmfn, 'load_object')
            self.call_object(obj, 'create')
            self.objects[pwmfn] = obj

        return self.objects[pwmfn]
        
    def clone_object(self, pwmfn):
        cls = self.load_class(pwmfn)
        objname = "%s#%s" % (pwmfn, self.next_guid())
        obj = cls(objname, 'clone_object')
        self.call_object(obj, 'create')
        self.objects[objname] = obj
        return obj

    def call_object(self, obj, method, *args, **kwargs):
        obj = self.objref2real(obj)
        self.object_stack.append(obj.get_objname())
        val = getattr(obj, method)(*args, **kwargs)
        del self.object_stack[-1]
        return val
    
    def start_call(self, obj, method, *args, **kwargs):
        self.object_stack = []
        # FIXME: Catch any errors sensibly
        return self.call_object(obj, method, *args, **kwargs)

    def objref2real(self, objref):
        if type(objref) is str:
            return self.objects[objref]
        return objref
        
    def efun_call_object(self, obj, method, *args, **kwargs):
        return self.call_object(obj, method, *args, **kwargs)
    
    def efun_load_class(self, path):
        return self.load_class(path)

    def efun_load_object(self, path):
        return self.load_object(path).get_objname()

    def efun_clone_object(self, path):
        return self.clone_object(path).get_objname()

    def efun_send_message(self, message):
        current_object = self.object_stack[-1]
        # Obj must be interactive so find it in the connection list
        # FIXME: How should this be optimised?
        for fd, data in self.connections.items():
            handler, objname = data
            if objname == current_object:
                handler.send_message(message)
                break
        else:
            raise errors.ObjectNotInteractive('passed object is not interactive')
        

        
    def network_connect(self, handler):
        socket = handler.transport.get_extra_info('socket')
        fd, raddr, laddr = socket.fileno(), socket.getpeername(), socket.getsockname()
        # FIXME: Should be wrapped in something that catches errors
        objname = self.start_call(self.config.controller, 'network_connect', raddr, laddr)
        # FIXME: Don't assume connect() always returns an object or None
        if objname is None:
            # abort
            return

        self.connections[fd] = (handler, objname)
        self.start_call(objname, 'network_connect')

    def network_disconnect(self, handler):
        # FIXME: Error safety?
        fd = handler.transport.get_extra_info('socket').fileno()
        self.start_call(self.connections[fd][1], 'network_disconnect')
        del self.connections[fd]

    def network_message(self, message, handler):
        fd = handler.transport.get_extra_info('socket').fileno()
        self.start_call(self.connections[fd][1], 'network_message', message)

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

