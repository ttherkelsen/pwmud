# This file contains file adapter classes.  At least one of these classes
# must be used in the config file for PWMud; the same class may be used
# multiple times.

import errors

class FileAdapterResult:
    def __init__(self, adapter, path, data=None):
        self.adapter = adapter
        self.path = path
        self.data = data

    def basename(self):
        raise NotImplementedError()

class FileAdapter:
    def valid_path(self, path):
        raise NotImplementedError()

    def load_file(self, path):
        raise NotImplementedError()

    def save_file(self, path, data):
        raise NotImplementedError()

    def __init__(self, path):
        raise NotImplementedError()

class OSFileAdapterResult(FileAdapterResult):
    def basename(self):
        return self.path.split("/")[-1]
    
class OSFileAdapter(FileAdapter):
    """
    This file loader loads files from the OS filesystem, relative to
    the specified base dir.

    For example, this code:

        fl = OSFileAdapter("/foo/bar")
        file = fl.load_file("/baz.txt")

    Would attempt to read the file /foo/bar/baz.txt from the OS filesystem.
    """

    def __init__(self, basedir):
        self.basedir = basedir

    def valid_path(self, path):
        """
        Return True if path is valid or raise InvalidPath() if it is not.

        path is a sequence of path segments, separated by, and starting
        with "/".  A segment cannot be any of the following strings:

          ""
          "."
          ".."

        Examples of valid paths:

          "/foo/bar"
          "/apple.txt"
          "/#/1/!/~"
          "/home/john/.bashrc"

        Examples of invalid paths:

          "foo/bar"          (does not begin with "/")
          "//banana.py"      (has an empty path segment)
          "/foo/../baz.txt"  (has a ".." segment)
        """
        if path == "/":
            raise errors.InvalidPath('path cannot be "/"')

        if not path.startswith("/"):
            raise errors.InvalidPath('path must start with "/"')

        parts = path[1:].split("/")
        if "" in parts or "." in parts or ".." in parts:
            raise errors.InvalidPath('path contains one or more "//", "." or ".." strings')

        return True
    
        
    def load_file(self, path):
        self.valid_path(path)
        ospath = self.basedir + path
        error = None
        try:
            with open(ospath, 'r') as fd:
                return OSFileAdapterResult(self, path, fd.read())
        except FileNotFoundError:
            error = errors.FileNotFound(path)
        except PermissionError:
            error = errors.AccessDenied(path)
        raise error

        
    def save_file(self, path, data):
        self.valid_path(path)
        ospath = self.basedir + path
        try:
            with open(ospath, 'w') as fd:
                return fd.write(data)
        except FileNotFoundError:
            raise errors.FileNotFound(path)
        except PermissionError:
            raise errors.AccessDenied(path)
