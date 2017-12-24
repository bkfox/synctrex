from synctrex.register import Register
from synctrex.base import Named


class Syncs(Register):
    key = 'name'


syncs = Syncs()
"""
Default register for Sync instances.
"""


class Sync(Named):
    """
    Define a synchronisation between a :py:attr:source and and a
    :py:attr:dest.
    """
    name = ''
    """
    Name used to manipulate and select Sync instances.
    """
    require = []
    """
    Synchronisation dependencies
    """
    method = None
    """
    Method instance to use
    """
    groups = []
    """
    Groups Sync belongs to
    """
    source = ""
    """
    Address/URI of data to copy from FIXME
    """
    files = []
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

    def __init__(self, method, register = syncs, clone_from = None,
                 **kwargs):
        """
        :params method: method to apply when running this sync
        :params register: register the Sync to this register
        :params clone_from: get default values from this Sync;
        """
        if clone_from:
            self.__dict__.update({
                k: getattr(clone_from, k)
                    for k, v in vars(clone_from.__dict__)
                        if not k.startswith('_')
            })
        self.__dict__.update(kwargs)
        register.register(self)

        self.require = self.require or []


    def run(self):
        """
        If yet running, return immediately

        :returns: :py:meth:method.run's call return.
        """
        if not self.method:
            return 0
            raise ValueError('no method assigned')

        if not self.method.is_available():
            raise ValueError('method not available')

        return self.method.run(self)


