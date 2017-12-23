from threading import Lock

from synctrex.register import Register
from synctrex.base import Named


class Syncs(Register):
    key = 'name'


syncs = Syncs()
"""
Default register for Sync instances.
"""


# FIXME: graph cycle is guaranteed only when dependencies are set at the
# sync instanciation. Avoid further write of require (with read property
# of a tuple) in order to avoid to implement graph cycles detection?

class Sync(Named):
    """
    Instance of Sync are registered to Syncs at ``__init__``.
    """
    name = ''
    """
    Name used to manipulate and select Sync instances.
    """
    require = []
    """
    Synchronisation dependencies
    """
    groups = []
    """
    Groups Sync belongs to
    """
    source = ""
    """
    Address/URI of data to copy from FIXME
    """
    include = []
    """
    List of files to synchronise (depends on method used)
    """
    exclude = ""
    """
    Exclude those files from synchronisation (depends on method used)
    """
    dest = ""
    """
    Address/URI of destination directory FIXME
    """
    dir = ""
    """
    Subdirectory to copy data into
    """
    method = None
    """
    Method instance to use
    """

    def __init__(self, register = syncs, clone_from = None, **kwargs):
        """
        :param inherit: copy attributes from this sync
        """
        if clone_from:
            self.__dict__.update({
                k: getattr(clone_from, k)
                    for k, v in vars(clone_from.__dict__)
                        if not k.startswith('_')
            })
        self.__dict__.update(kwargs)
        register.register(self)

        if self.source: self.source = Address(self.source)
        if self.dest: self.dest = Address(self.dest)

        # require is read only
        self.Lock = Lock()

    def run(self):
        """
        If yet running, return immediately

        :returns: :py:meth:method.run's call return.
        """
        self.log('start sync')
        import time
        time.sleep(len(self.name)*3)
        return 0


