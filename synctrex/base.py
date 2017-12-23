
class Named:
    """
    Class whose instances are named. Also provide logging
    """
    name = ''

    def log(self, log, *args, **kwargs):
        print('[' + type(self).__name__, '/', self.name + ']',
              log.format(*args, **kwargs))


