import itertools
import os
import psutil
import urllib.parse


class Address(str):
    url = None

    def __new__(cls, url, *path):
        s = str.__new__(cls, url)
        if path:
            s = os.path.join(s, path)
        s.url = urllib.parse.urlparse(url)
        return s

    def is_remote(self):
        """
        Return True if address points to a remote resource.
        """
        return self.url.scheme not in ('file', 'dev')

    def is_dev(self):
        """
        Return True if address points to a block device.
        """
        if self.url.scheme == 'dev':
            return True
        fstat = os.stat(self)
        return stat.S_ISBLK(fstat.st_mode)

    def mount_point(self):
        """
        Return mount point of the device when it targets a local file.
        """
        parts = psutil.disk_partitions()
        if self.is_dev():
            try:
                return next(( p.mountpoint
                                for p in parts
                                    if x.device == self
                ))
            except:
                return ''

        mountpoint = ''
        for p in parts:
            if self.startswith(p.mountpoint) and \
                    len(p.mountpoint) > mountpoint:
                mountpoint = p.mountpoint
        return mountpoint


#class Address(URI):
#    """
#    Abstract class to represent an uri. Used in order to allow extra
#    info on an URI

#    The address follow the given form:
#        - uri:      (protocol '://')? address
#        - protocol: string of max 13 chars
#        - address:  ((user '@')? host ':') post

#    When there is no protocol specified, use 'file://' prefix
#    """
#    def __new__(cls, value, address_info = None):
#        s = str.__new__(cls, value)
#        if address_info:
#            s.address_info = address_info
#        return s

#    @property
#    def protocol(self):
#        """
#        Return protocol of the address. If not specified, is 'file'
#        """
#        if '://' in self[:16]:
#            n = self.index('://')
#            return self[:n]
#        return 'file'

#    @property
#    def address(self):
#        """
#        Complete address without the protocol(include remote host, etc.)
#        """
#        if '://' in self[:16]:
#            n = self.index('://')
#            return self[n+3:]
#        return self

#    @property
#    def address_info(self):
#        """
#        Return a dict that describe the address components.
#        """
#        if not self.is_remote():
#            return { 'remote': False, 'protocol': self.protocol,
#                     'user': None, 'host': None, 'path': self.address }

#        user, *host = self.address.split('@', 1)
#        if host:
#            host = host[0]
#        else:
#            host = user
#            user = None

#        if ':' in host:
#            host, *path = host.split(':', 1)

#        if path:
#            path = path[0]
#        else:
#            path = None
#        return { 'remote': True, 'protocol': self.protocol,
#                 'user': user, 'host': host, 'path': path}

#    @address_info.setter
#    def address_info(self, value):
#        r = Address(value['protocol'] + '://')
#        if value.get('host'):
#            if value.get('user'):
#                r += value['user'] + '@' + value['host']
#            else:
#                r += value['host']
#            if value.get('path'):
#                r += ':' + value['path']
#        else:
#            r += value['path']
#        self = r

#    def is_dir(self):
#        """
#        Return true if file is a directory.
#        """
#        return os.path.isdir(self)

#    def is_blk(self):
#        """
#        Return True if the file is a device block.
#        """
#        if self.protocol == 'dev':
#            return True
#        fstat = os.stat(self)
#        return stat.S_ISBLK(fstat.st_mode)

#    def get_mount_point(self):
#        """
#        Return the mount point of the Address if the file is a block
#        device.
#        """
#        if not self.is_blk():
#            return

#        with open('/proc/mounts', 'r') as file:
#            for line in file.readlines():
#                if line.startswith(self):
#                    #FIXME: mount points with spaces, special mount points?
#                    return line.split(' ')[1]

#    def is_remote(self):
#        """
#        Return true if the address is an uri
#        """
#        return self.protocol not in ['file', 'dev']

#    def exists(self):
#        """
#        Return os.path.exists(self). Assume that the address is a regular
#        file path.
#        """
#        return os.path.exists(self)

#    def join(self, path):
#        """
#        Return an address with the given path appended
#        """
#        if not self.is_remote():
#            return Address(os.path.join(self, path))

#        info = self.address_info
#        info['path'] = os.path.join(info['path'] or '.', path)
#        return Address(address_info = info)

#    def check(self):
#        """
#        Check if the address is okay. If an error occurs, return it.
#        """
#        if not self.is_remote() and not self.address.exists():
#            return [Error(self, 'file does not exists')]

#        if self.is_blk() and not self.address.get_mount_point():
#            return [Error(self, 'device not mounted')]



