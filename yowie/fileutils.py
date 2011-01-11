from urllib2 import urlopen, urlparse, URLError

from django.conf import settings
from django.core.files.utils import FileProxyMixin

__all__ = [
    "open_url",
    "LimitedFileSizeOverflow",
    "LimitedFile"
]

def open_url(url):
    """
    open_url(url) - open url and return file descriptor

    url argument examples:

    /home/praetorian/secret.txt
    file:///home/praetorian/secret.txt
    http://domain.tld/secret.txt
    ftp://domain.tld/secret.txt
    """
    bits = urlparse.urlsplit(url)

    if bits.scheme in ('', 'file'):
        fd = open(bits.netloc + bits.path, 'rb')
    elif bits.scheme in ('http', 'ftp'):
        fd = urlopen(bits.geturl())
    else:
        raise URLError("Unsupported protocol '%s'" % bits.scheme)

    return fd


class LimitedFileSizeOverflow(Exception):
    pass

class LimitedFile(FileProxyMixin):
    """
    File-like object wrapper which raise LimitedFileSizeOverflow
    exception if file content length is greater then limit. Default limit is
    settings.LIMITEDFILE_MAX_SIZE bytes or 10MB, if setting doesn't exist.

    LimitedFile(file_descriptor, limit=None)
    """

    _limit = getattr(settings, 'LIMITEDFILE_MAX_SIZE', 10*1024*1024)

    def __init__(self, file, limit=None):
        self.file = file
        self.limit = limit or self._limit
        self.total = 0

    def _normalize_size(self, size):
        if not size or size < 0 or size > self.limit:
            size = self.limit + 1

        rest = self.limit - self.total
        if size > rest:
            size = rest + 1

        return size

    def read(self, size=None):
        " read(self [, size]) "
        content = super(LimitedFile, self).read(self._normalize_size(size))
        self.total += len(content)

        if self.total > self.limit:
            raise LimitedFileSizeOverflow('File content is too long')

        return content

    def readline(self, size=None):
        " readline(self [, size]) "
        content = super(LimitedFile, self).readline(self._normalize_size(size))
        self.total += len(content)

        if self.total > self.limit:
            raise LimitedFileSizeOverflow('File content is too long')

        return content

    def readlines(self, sizehint=None):
        " readlines(self [, sizehint]) "
        content = self.read(self._normalize_size(sizehint))

        lines = []
        while content:
            index = content.find('\n')

            if index >= 0:
                lines.append(content[0:index + 1])
                content = content[index + 1:]
            else:
                lines.append(content)
                break

        return lines
