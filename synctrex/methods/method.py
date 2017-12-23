import datetime
import subprocess

try:
    from rst2ansi import rst2ansi
except ImportError:
    rst2ansi = None


from synctrex.register import Register
from synctrex.base import Named


class Methods(Register):
    key = 'name'
    by_proto = {}

    @classmethod
    def register(cl, item, key = None):
        super().register(item, key)
        if item.protocols:
            for protocol in item.protocols:
                r = cls.by_proto.setdefault(protocol, [])
                r.append(cl)

    @classmethod
    def by_proto(cl, key, default = None)
        return self.by_proto.get(key, default)


class Method(Named):
    """
    """
    protocols = []
    """
    [class attribute] Protocols supported by the method
    """

    @classmethod
    def is_available(cl):
        """
        Return True if the method can be used accounted the runtime
        environment.
        """
        raise NotImplementedError

    def can_parallelize(self, method):
        """
        Returns True if the given method can be run concurrently. This
        allows to run concurrent methods when it is not recommended
        (e.g. on the same device with regular hdd)
        """
        raise NotImplementedError

    def extra_info(self):
        """
        Return extra informations to print out in :py:meth:`info`
        """
        return ''

    def info(self):
        """
        Return info string to be used as help. Basically, it just
        returns the docstring and extra information.

        If rst2ansi is present, convert info from RST to ANSI and extra
        info.
        """
        doc = \
        """
        {name}
        ~~~~~~
        - Available: {available}
        - Protocols: {protocols}

        {extra}

        Doc string
        ----------
        {doc}
        """.format(
            name = self.name,
            available = self.is_available(),
            protocols = ', '.join(self.protocols)
            extra = self.extra,
            doc = self.__doc__
        )
        return rst2ansi(doc) if rst2ansi else doc

    def run(self, sync):
        raise NotImplementedError


class ExecMethod(Method):
    program = ''
    """
    [class attribute] Filename of the program that is executed to run
    synchronisation. It will be searched using ``PATH`` environment
    variable.
    """
    args = None
    """
    Array of arguments to pass as is to the subprocess.
    """

    @classmethod
    def is_available(cl):
        paths = os.getenv('PATH').split(':')
        for path in paths:
            path = os.path.join(path, cl.program)
            if os.path.exists(path):
                return True
        return False

    def get_args(self, sync):
        """
        Return argument to pass to process (excluding program name).
        """
        raise NotImplementedError

    def has_failed(self, exit_code):
        """
        Return True if the synchronisation has failed based on exit_code.
        """
        raise NotImplementedError

    def run(self, sync):
        # FIXME: clean up
        args = [self.program] + [self.get_args(sync)]
        self.log("sync {}: {} -> {}", sync.name,
                 sync.source.address, sync.dest.address)
        duration = datetime.datetime.now()
        exit_code = subprocess.call(args)
        duration = datetime.datetime.now() - duration
        self.log("sync {}: exit code is {}, process took {} secs",
                 sync.name, exit_code, duration)

        if self.has_failed(exit_code):
            raise subprocess.CalledProcessError(
                "sync {} failed with exit code {}"
                .format(sync.name, exit_code)
            )

