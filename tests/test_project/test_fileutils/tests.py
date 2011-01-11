from StringIO import StringIO
from urllib2 import URLError

from django.conf import settings
from django.test import TestCase

from yowie import LimitedFile, LimitedFileSizeOverflow, open_url

class TestLimitedFile(TestCase):
    content = "0123456789\nABCDEFGHIJ\nKLMNOPQRST"

    def setUp(self):
        self.fd = StringIO(self.content)

    def test_default_read(self):
        f = LimitedFile(self.fd)
        self.assertEquals(f.read(), self.content)
        self.assertEquals(f.total, 32)

    def test_limited_read_pass(self):
        f = LimitedFile(self.fd, 32)
        self.assertEquals(f.read(), self.content)
        self.assertEquals(f.total, 32)

    def test_limited_read_fail(self):
        f = LimitedFile(self.fd, 10)
        self.assertRaises(LimitedFileSizeOverflow, f.read)
        self.assertEquals(f.total, 11)

    def test_limited_chunk_read_pass(self):
        f = LimitedFile(self.fd, 32)
        self.assertEquals(f.read(15), self.content[:15])
        self.assertEquals(f.read(15), self.content[15:30])
        self.assertEquals(f.read(15), self.content[30:])
        self.assertEquals(f.read(), '')
        self.assertEquals(f.total, 32)

    def test_limited_chunk_read_fail(self):
        f = LimitedFile(self.fd, 20)
        self.assertEquals(f.read(10), self.content[:10])
        self.assertEquals(f.read(10), self.content[10:20])
        self.assertRaises(LimitedFileSizeOverflow, f.read, 10)
        self.assertEquals(f.total, 21)

    def test_default_readline(self):
        f = LimitedFile(self.fd)
        self.assertEquals(f.readline(), '0123456789\n')
        self.assertEquals(f.readline(), 'ABCDEFGHIJ\n')
        self.assertEquals(f.readline(), 'KLMNOPQRST')
        self.assertEquals(f.readline(), '')
        self.assertEquals(f.total, 32)

    def test_default_readline_pass(self):
        f = LimitedFile(self.fd, 32)
        self.assertEquals(f.readline(), '0123456789\n')
        self.assertEquals(f.readline(), 'ABCDEFGHIJ\n')
        self.assertEquals(f.readline(), 'KLMNOPQRST')
        self.assertEquals(f.readline(), '')
        self.assertEquals(f.total, 32)

    def test_default_readline_fail(self):
        f = LimitedFile(self.fd, 15)
        self.assertEquals(f.readline(), '0123456789\n')
        self.assertRaises(LimitedFileSizeOverflow, f.readline)
        self.assertEquals(f.total, 16)

    def test_limited_chunk_readline_pass(self):
        f = LimitedFile(self.fd, 32)
        self.assertEquals(f.readline(15), '0123456789\n')
        self.assertEquals(f.readline(5), 'ABCDE')
        self.assertEquals(f.readline(5), 'FGHIJ')
        self.assertEquals(f.readline(5), '\n')
        self.assertEquals(f.readline(15), 'KLMNOPQRST')
        self.assertEquals(f.readline(15), '')
        self.assertEquals(f.total, 32)

    def test_limited_chunk_readline_fail(self):
        f = LimitedFile(self.fd, 22)
        self.assertEquals(f.readline(15), '0123456789\n')
        self.assertEquals(f.readline(15), 'ABCDEFGHIJ\n')
        self.assertRaises(LimitedFileSizeOverflow, f.readline, 15)
        self.assertEquals(f.total, 23)

    def test_default_readlines(self):
        f = LimitedFile(self.fd)
        self.assertEquals(f.readlines(), ['0123456789\n', 'ABCDEFGHIJ\n', 'KLMNOPQRST'])
        self.assertEquals(f.readlines(), [])
        self.assertEquals(f.total, 32)

    def test_limited_readlines_pass(self):
        f = LimitedFile(self.fd, 32)
        self.assertEquals(f.readlines(), ['0123456789\n', 'ABCDEFGHIJ\n', 'KLMNOPQRST'])
        self.assertEquals(f.readlines(), [])
        self.assertEquals(f.total, 32)

    def test_limited_readlines_fail(self):
        f = LimitedFile(self.fd, 25)
        self.assertRaises(LimitedFileSizeOverflow, f.readlines)
        self.assertEquals(f.total, 26)

    def test_limited_chunk_readlines_pass(self):
        f = LimitedFile(self.fd, 25)
        self.assertEquals(f.readlines(25), ['0123456789\n', 'ABCDEFGHIJ\n', 'KLM'])
        self.assertEquals(f.total, 25)

    def test_limited_chunk_readlines_fail(self):
        f = LimitedFile(self.fd, 25)
        self.assertEquals(f.readlines(25), ['0123456789\n', 'ABCDEFGHIJ\n', 'KLM'])
        self.assertRaises(LimitedFileSizeOverflow, f.readlines, 25)
        self.assertEquals(f.total, 26)

class TestOpenUrl(TestCase):
    def test_open_url_file_absolute_path(self):
        fd = open_url(settings.EXAMPLE_RSS_FEED)
        self.assertEquals('<?xml', fd.read(5))

    def test_open_url_file_with_protocol(self):
        fd = open_url('file://%s' % settings.EXAMPLE_RSS_FEED)
        self.assertEquals('<?xml', fd.read(5))

    def test_open_url_http(self):
        # TODO:
        self.skipTest("Not implemented")

    def test_open_url_fail(self):
        self.assertRaises(URLError, open_url, 'ssh://domain.tld')
