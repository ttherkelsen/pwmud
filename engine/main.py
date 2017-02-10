import argparse, os.path, sys, traceback, json, inspect, logging, inspect

import network.loop, errors, file_adapters

# Efun imports

class Engine(object):
    version = 'PWMud 0.1a'
    class config: pass

    def __init__(self, args):
        self.config_file = args.config
        self.debug_log_file = args.logfile
        self.console_log_level = logging.getLevelName(args.console_log_level)
        self.console_debug_names = [ t for t in args.console_debug_names.split(",") if t ]
        self.setup_logging()

    def setup(self):
        self.objects = {}
        self.classes = {}
        self.builtins = {
            '__build_class__': __builtins__.__build_class__,
            'py': __builtins__,
            'super': __builtins__.super,
            '__name__': 'engine',

            # Core functionality
            'load_class': self.efun_load_class,
            
            # Object instantiation
            'clone_object': self.efun_clone_object,
            'load_object': self.efun_load_object,

            # Network interface
            'send_message': self.efun_send_message,

            # Logging
            'log': self.efun_log,
            
        }
        self.connections = {}
        self.guid = 0
        self.object_stack = []

    def setup_logging(self):
        # 1 - All logging goes to the logging file (default pwmud.log)
        # 2 - INFO or higher goes to the screen (stderr)
        # 3 - Selected names, regardless of level, goes to the screen (stderr)
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        fh = logging.FileHandler(self.debug_log_file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s'))
        root.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setLevel(self.console_log_level)
        sh.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
        root.addHandler(sh)

        def console_log_filter(rec):
            if rec.levelno >= self.console_log_level:
                return False # Already emitted
            
            for name in self.console_debug_names:
                if name in rec.name:
                    return True

            return False
        
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(logging.Formatter('%(asctime)s [%(name)s] %(message)s'))
        sh.addFilter(console_log_filter)
        root.addHandler(sh)

        
        
    def run(self):
        self.log("%s started" % self.version)
        self.debug("Setting up")
        self.setup()
        self.debug("Loading config")
        self.load_config()
        self.debug("Loading controller object")
        self.load_object(self.config.controller)

        self.debug("Running controller.init()")
        self.start_call(self.config.controller, 'init')

        self.debug("Starting network loop")
        network.loop.run(self)
        self.debug("Network loop ended, performing final cleanup before exiting")

        # FIXME: Do stuff ;-)

        self.log("%s stopped" % self.version)

    def debug(self, msg, name=None, funcname=True, callstack=1):
        if name is None:
            name = 'pwmud.engine'
        if funcname:
            name += "."+ inspect.stack()[callstack].function
        self.log(msg, name, logging.DEBUG)

    def log(self, msg, name=None, level=logging.INFO):
        if name is None:
            name = 'pwmud.engine'
        logger = logging.getLogger(name)
        logger.log(level, msg)
        

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
            raise errors.ObjectNotInteractive('current object is not interactive')
        
    def efun_log(self, message):
        self.debug('%s:%s' % (self.objref2real(self.object_stack[-1]).get_objname(), message), 'pwmud.library', callstack=2)
        
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
    cmdline = argparse.ArgumentParser(description="Run a PWMud.")
    cmdline.add_argument(
        '-v', '--version', action="version", version=Engine.version,
        help='Print version and exit.'
    )
    cmdline.add_argument(
        '-l', '--logfile', default="pwmud.debug.log",
        help='Which file to log debug info to, defaults to "pwmud.debug.log".'
    )
    cmdline.add_argument(
        '-c', '--console-log-level',
        default='INFO', choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
        help='Minimum logging level, defaults to "INFO", legal levels: DEBUG INFO WARNING ERROR CRITICAL.'
    )
    cmdline.add_argument(
        '-d', '--console-debug-names',
        default='',
        help='Which log names to always print to console, regardless of log level.  Matching is simple substring.  Separate multiple names with ",".'
    )
    cmdline.add_argument('config', help='Path to config file')
    args = cmdline.parse_args()

    engine = Engine(args)
    engine.run()

