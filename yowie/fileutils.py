from urllib2 import build_opener, ProxyHandler, urlparse, URLError

from django.conf import settings
from django.core.files.utils import FileProxyMixin

__all__ = [
    "open_url",
    "LimitedFileSizeOverflow",
    "LimitedFile"
]

def open_url(url, **kwargs):
    """
    open_url(url, **kwargs) - open url and return file descriptor

    url - local file path or full url path. Allowed protocols are local file
    path, file, http and ftp

    kwargs - additional attributes according to protocol, 'mode' for local
    path and file protocol, 'proxy', 'data' and 'timeout' (Python >= 2.6)
    for http and ftp protocols

    Examples:

    open_url('/home/praetorian/secret.txt')
    open_url('file:///home/praetorian/secret.txt', mode='r')
    open_url('http://domain.tld/secret.txt', proxy='172:16:1:100:8000')
    open_url('ftp://domain.tld/secret.txt')
    """
    bits = urlparse.urlsplit(url)
    attrs = kwargs

    if bits.scheme in ('', 'file'):
        url = bits.netloc + bits.path
        opener = open
    elif bits.scheme in ('http', 'ftp'):
        handlers = []
        if 'proxy' in attrs:
            handlers.append(ProxyHandler({bits.scheme: attrs.pop('proxy')}))

        url =  bits.geturl()
        opener = build_opener(*handlers).open
    else:
        raise URLError("Unsupported protocol '%s'" % bits.scheme)

    return opener(url, **attrs)


class LimitedFileSizeOverflow(Exception):
    pass

class LimitedFile(FileProxyMixin):
    """
    File-like object wrapper which raise LimitedFileSizeOverflow
    exception if file content length is greater than limit. Default limit is
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

    @staticmethod
    def open_url(url, limit=None, **kwargs):
        """
        open_url(url [, limit [, **kwargs]]) - staticmethod, open url and
        return file descriptor

        url - url to opening, can be local file path, file://...,
        http://... and ftp://...

        limit - raise LimitedFileSizeOverflow exception if file content
        length is greater then limit

        kwargs - additional attributes according to protocol, 'mode' for
        local path and file protocol, 'proxy', 'data' and
        'timeout' (Python >= 2.6) for http and ftp protocols.

        Examples:

        LimitedFile.open_url('/home/praetorian/secret.txt')
        LimitedFile.open_url('file:///home/praetorian/secret.txt', mode='r')
        LimitedFile.open_url('http://domain.tld/secret.txt',
                             limit=1024*1024, proxy='172:16:1:100:8000')
        LimitedFile.open_url('ftp://domain.tld/secret.txt')
        """
        return LimitedFile(open_url(url, **kwargs), limit)

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

    def next(self):
        " next(self) "
        line = self.readline()
        if not line:
            raise StopIteration()
        return line

    def close(self):
        self.file.close()

    @property
    def closed(self):
        return self.file.closed
