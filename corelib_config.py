# You must specify at least one file adapter; it is through these
# that the engine will access game library files, including the class
# definition files.
# The engine will try each file adapter in the order specified below, until
# one of them returns a string (the file contents).
# Please read the documentation in engine/file_adapters.py for more
# information. (FIXME: Better description)
file_adapters = [
    OSFileAdapter('/raid/www/lowtek.dk/pwmud-dev-live/corelib'),
#    ZipFileAdapter('/raid/www/lowtek.dk/pywebmud/testarchive.zip'),
#    URLFileAdapter('http://lowtek.dk/static/'),
]

# Controller object (as a PWMud Object name)
controller = '/core/controller'

# Which path to write object data to.
# NOTE: Must be an absolute path and it must exist already
# FIXME: This should be done with an adapter
#save_path = OSPersistenceAdapter()
save_path = '/raid/www/lowtek.dk/pwmud-dev-live/corelib.data'

# Which IP address to listen on (use 0.0.0.0 to listen on all local IPs)
listen_ip = '0.0.0.0'

# Which TCP port to listen on (must be integer between 1024 and 65335) 
listen_port = 4000

# Interval (in seconds) between each call to housekeeping()
housekeeping_interval = 1.0

