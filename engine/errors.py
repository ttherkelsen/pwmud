class EngineError(Exception): pass
class ExecError(EngineError): pass
class ClassNotFound(ExecError): pass

class FileAdapterError(EngineError): pass
class InvalidPath(FileAdapterError): pass
class FileNotFound(FileAdapterError): pass
class AccessDenied(FileAdapterError): pass
